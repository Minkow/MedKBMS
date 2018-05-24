from flask import render_template, redirect, url_for, request, flash, abort, send_file, jsonify
from flask_login import current_user, login_required, login_user, logout_user
#from py2neo import *
from py2neo import Graph, NodeSelector, Node, Relationship
from py2neo.ogm import GraphObject, Property
from app import app, db
from app.models import *
from app.forms import *
from flask_nav import Nav
from flask_nav.elements import *
import os

path = 'D:/ex1/'

#Resource / ns0__label
@app.route('/', methods=['POST', 'GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = SearchForm(request.form)
#    if current_user.role == 'Manager':
#        courses = current_user.courses
#    elif current_user.role == 'User':
#        courses = current_user.teachings
    if request.method == 'POST':
        # if form.submit_btn.data and form.validate_on_submit():
        #     Stext = form['context'].data
        #     return redirect(url_for('search', result=Stext))
        # if form.add_btn and form.validate_on_submit():
        #     return redirect(url_for('add'))
        Stext = request.form['text']
        return redirect(url_for('search', result=Stext))
    return render_template('index.html', form = form, username = current_user.username, active=1)

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST':
        #if form.submit_btn.data and form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        #print(password)
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username not found', 'error')
        elif not user.check_password(password):
            flash('Username or password incorrect', 'error')
        else:
            login_user(user)
            return redirect(url_for('index'))
        # if form.regist_btn.data and form.validate_on_submit():
        #     return redirect(url_for('register'))
    return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have logged out')
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if request.method == 'POST':
        hash = hashlib.md5()
        hash.update(request.form['password'].encode('utf-8'))
        # user = User(username=form.username.data, password=hash.hexdigest(), role='User')
        user = User(username=request.form['username'], password=hash.hexdigest(), role='User')
        db.session.add(user)
        db.session.commit()
        flash('Regist Success','success')
        return redirect(url_for('index'))
    return render_template('register.html',form=form)

@app.route('/search=<result>',methods=['POST','GET'])
@login_required
def search(result):
    graph = Graph(password = "123456") #password:need to be edited
    selector = NodeSelector(graph)
    if(result.startswith('lld:')):
        URI = result
    else:
        URI = "file:///D:/ex1/t1/" + result
    node = Search.getnode(graph=graph, text=URI)
    if node == [] and result.strip(' ') != '':
        cql = "match(n) where n.ns0__label=~'.*" + result + ".*' return n limit 15"
        res = graph.run(cql).data()
        result = []
        for i in res:
            print(i)
            result.append(getnodename(i.get('n')))
        if result != []:
            return render_template('searchabout.html', result=result, username=current_user.username, active=0)
    form = ReturnForm(request.form)
    global link, page, leng
    if (node):
        #print(node)
        result = result
        link, page, leng = Search.getrelation(graph, node)
    else:
        result = 'Not Found'
        link = ''
        page = ''
        leng = ''
    if form.return_btn.data and form.validate_on_submit():
        return redirect(url_for('index'))
    if form.edit_btn.data and form.validate_on_submit():
        if current_user.role == 'Manager':
            return redirect(url_for('edit', result = result))
        else:
            flash('You are not database manager','error')
    return render_template('search.html', result = result, link = link, page = page, leng = leng, form = form, username = current_user.username, active=0)

@app.route('/advsearch',methods=['POST','GET'])
def advsearch():
    graph = Graph(password = "123456") #password:need to be edited
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        Stext1 = request.form['text1']
        Stext2 = request.form['text2']
        if (Stext1.startswith('lld:')):
            URI1 = Stext1
        else:
            URI1 = "file:///D:/ex1/t1/" + Stext1
        if (Stext2.startswith('lld:')):
            URI2 = Stext2
        else:
            URI2 = "file:///D:/ex1/t1/" + Stext2

        node1 = Search.getnode(graph=graph, text=URI1)
        node2 = Search.getnode(graph=graph, text=URI2)
        if node1 == [] or node2 ==[]:
            flash('Node not exists','warning')
            return redirect(url_for('advsearch'))
        ns,pa = Search.asearch(graph,URI1,URI2)
        return render_template('advsr.html',nodes = ns, path = pa, username = current_user.username, active=0)
    return render_template('advsearch.html', username = current_user.username, active=0)

@app.route('/edit=<result>',methods=['POST','GET'])
@login_required
def edit(result):
    if current_user.role != 'Manager':
        flash('You are not database manager', 'error')
        return redirect(url_for('index'))
    graph = Graph(password = "123456") #password:need to be edited
    selector = NodeSelector(graph)
    form = AddForm(request.form)
    if(result.startswith('lld:')):
        URI = result
    else:
        URI = "file:///D:/ex1/t1/" + result
    # if request.method == 'POST':
    #     if form.validate_on_submit():
    #         sname = form['snode'].data
    #         type  = form['relation'].data
    #         ename = form['enode'].data
    #         sURI = "file:///D:/ex1/t1/" + sname
    #         eURI = "file:///D:/ex1/t1/" + ename
    #         type = 'ns2__' + type
    #         snode = Search.getnode(graph=graph, text=sURI)
    #         enode = Search.getnode(graph=graph, text=eURI)
    node = Search.getnode(graph=graph, text=URI)
    form = ReturnForm1(request.form)
    global link, page, leng
    if (node):
        #print(node)
        result = result
        link, page, leng = Search.getrelation(graph, node)
    else:
        result = 'Not Found'
        link = ''
        page = ''
        leng = ''
    if form.return_btn.data and form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('edit.html', result = result, link = link, page = page, leng = leng, form = form, username = current_user.username, active=0)

@app.route('/add',methods=['POST','GET'])
@login_required
def add():
    print(current_user.role)
    if current_user.role != 'Manager':
        flash('You are not database manager', 'error')
        return redirect(url_for('index'))

    graph = Graph(password = "123456") #password:need to be edited
    selector = NodeSelector(graph)
    form = AddForm(request.form)
    #URI = "file:///D:/ex1/t1/" + result
    if request.method == 'POST':
        if form.validate_on_submit():
            sname = form['snode'].data
            typ  = form['relation'].data
            ename = form['enode'].data
            print(sname)
            sURI = "file:///D:/ex1/t1/" + sname
            eURI = "file:///D:/ex1/t1/" + ename
            type = 'ns2__' + typ
            #snode = Search.getnode(graph=graph, text=sURI)
            #enode = Search.getnode(graph=graph, text=eURI)
            username = current_user.username
            rel = Edit.relationadd(graph, sURI, type, eURI)
            pa = path + username + '.txt'
            fp = open(pa,'a+')
            fp.write('Add relationship:' + sname + '-' + typ + '->' + ename + '\n')
            fp.close()
            flash('Success!', 'success')
            #return redirect(url_for('search', result = sname))
            return redirect(url_for('index'))

    return render_template('add.html', form = form, username = current_user.username, active=0)

@app.route('/delete/<s>+<r>+<e>',methods=['POST','GET'])
@login_required
def delete(s, r, e): #delete one relationship
    form = SearchForm(request.form)
    graph = Graph(password = "123456") #password:need to be edited
    selector = NodeSelector(graph)
    if(r.startswith('->')):
        rel = r.split('>',1)[1].split(':',1)[0]
    else:
        rel = r.rstrip().rstrip(':')
        #print(rel)
    Edit.relationdelete(graph, selector, s, rel, e)
    username = current_user.username
    pa = path + username + '.txt'
    fp = open(pa, 'a+')
    fp.write('Delete relationship:' + s + '-' + rel + '->' + e + '\n')
    fp.close()
    flash('Success!', 'success')
    return redirect(url_for('index'))

@app.route('/passrel/<s>+<r>+<e>+<flag>', methods=['POST', 'GET'])
@login_required
def passrel(s, r, e, flag):
    graph = Graph(password="123456")  # password:need to be edited
    if(r.startswith('->')):
        rel = r.split('>',1)[1].split(':',1)[0]
    else:
        rel = r.rstrip().rstrip(':')
    glovar.editsnode = s
    glovar.editenode = e
    glovar.editrelation = rel
    if(flag==1):
        return render_template('editrel.html', s=s, r=rel, e=e, active=0, username = current_user.username)
    else:
        return render_template('editrel.html', s=e, r=rel, e=s, active=0, username = current_user.username)

@app.route('/edit/<s>+<r>+<e>', methods=['POST', 'GET'])
@login_required
def editrel(s, r, e):
    graph = Graph(password="123456")  # password:need to be edited
    selector = NodeSelector(graph)
    Edit.relationedit(graph, request.form['start'], request.form['relation'], request.form['end'])
    Edit.relationdelete(graph,selector, s, r, e)
    username = current_user.username
    pa = path + username + '.txt'
    fp = open(pa, 'a+')
    fp.write('Edited relationship from ' + s + '-' + r + '->' + e + 'to ' + request.form['start'] + '-' + request.form['relation'] + '->' + request.form['end'] + '\n')
    fp.close()
    return redirect(url_for('index'))

@app.route('/view=<result>', methods=['POST', 'GET'])
@login_required
def view(result):
    return render_template('view.html', result = result, username = current_user.username)

@app.route('/graph=<result>', methods=['POST', 'GET'])
@login_required
def getgraph(result):
    graph = Graph(password="123456")  # password:need to be edited
    selector = NodeSelector(graph)
    uri = name2uri(result)
    nodes = []
    edges = []
    t = Search.getnode(graph,uri)
    if t!=[]:
        print(t)
        nodes = [Search.buildnode(t,"origin")]
        n1,r,e1 = Search.getoutnode(graph, t)
        for i in range(len(r)):
            nodes = nodes +[Search.buildnode(n1[i],r[i])]
        # for i in Search.getoutnode(graph, t):
        #     nodes = nodes + [Search.buildnode(i['data'])]
        #     print(i)
        n2,e2 = Search.getinnode(graph, t)
        for i in n2:
            nodes = nodes + [Search.buildnode(i,"in")]
        # for i in Search.getoutnode(graph, t):
        #     nodes = nodes + [Search.buildnode(i,"out")]

        #edges = Search.buildedges(graph,t)
        edges = e1 + e2
        n = n1+n2
        # for i in n:
        #     for j in n:
        #         if i!=j:
        #             if(graph.match_one(start_node=i, end_node=j, bidirectional=False)!=None):
        #                 r=graph.match(start_node=i, end_node=j, bidirectional=False)
        #                 for k in r:
        #                     temp = str(k).split('-', 2)
        #                     sid = temp[0].strip('()')
        #                     eid = temp[2].strip('>()')
        #                     ty = k.type().split('_', 2)[2]
        #                     edges = edges + [{"data": {'source': sid, 'target': eid, 'relationship': ty}}]
        #holyfuck what's this!?
        #print(nodes)
        #print(edges)
    return jsonify(elements = {"nodes":nodes, "edges": edges})
    #URI = "file:///D:/ex1/t1/" + result
    # if request.method == 'POST':
    #     if form.validate_on_submit():
    #         sname = form['snode'].data
    #         type  = form['relation'].data
    #         ename = form['enode'].data
    #         print(sname)
    #         sURI = "file:///D:/ex1/t1/" + sname
    #         eURI = "file:///D:/ex1/t1/" + ename
    #         type = 'ns2__' + type
    #         #snode = Search.getnode(graph=graph, text=sURI)
    #         #enode = Search.getnode(graph=graph, text=eURI)
    #         rel = Edit.relationadd(graph, sURI, type, eURI)
    #         print(rel)
    #         #return redirect(url_for('search', result = sname))
    #         return redirect(url_for('index'))
    #return render_template('index.html',form = form, active=0)

