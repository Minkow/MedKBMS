from app import db
from flask_login import UserMixin
import hashlib
from datetime import datetime
import uuid
from py2neo import Graph, NodeSelector, Node, Relationship
from py2neo.ogm import GraphObject, Property
from app import app

def getnodename(node):
    if (node['ns0__label'] != None):
        name = node['ns0__label']
    else:
        name = (node['uri'].split('/', 6))[6].split('"')[0]
    return name

def name2uri(s):
    if(s.startswith('lld:')):
        s = s
    else:
        s = glovar.uripath + s
    return s

def uri2name(s):
    s = (s.split('/', 6))[6].split('"')[0]
    return s

class glovar():
    editsnode = ''
    editenode = ''
    editrelation = ''
    uripath = 'file:///D:/ex1/t1/'
#pass paras to input.value showed on editrel.html

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
 #   name = db.Column(db.String(256))
    username = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
    role = db.Column(db.Enum('Manager', 'User'))

    def check_password(self, password):
        s = hashlib.md5()
        s.update(password.encode('utf-8'))
        return self.password == s.hexdigest()

class Resource(GraphObject):
    __primarykey__ = 'uri'

    uri = Property()
    ns0__label = Property()

class Search(Graph, NodeSelector, Node, Relationship):
    def getnode(graph, text): #input name
        cql = "MATCH (n{uri:'" + text + "'}) return n"
        res = graph.run(cql).data()
        #print(res)
        if(res):
            node = res[0].get('n')
        else:
            node = []
        return node

    def getrelation(graph, node):
        relations = graph.match(start_node=node, bidirectional=True)
        link1 = []
        link2 = []
        page1 = []
        page2 = []
        for i in relations:
            print(i)
            type = i.type().split('_', 2)[2]
            snode = i.start_node()
            enode = i.end_node()
            print(snode)
            print(enode)
            sname = (snode['uri'].split('/', 6))[6].split('"')[0]
            if(enode['uri'].startswith('lld:')):
                ename = enode['uri']
            else:
                #ename = (enode['uri'].split('/', 6))[6].split('"')[0]
                if(enode['ns0__label']!=None):
                    ename = enode['ns0__label']
                else:
                    ename = (enode['uri'].split('/', 6))[6].split('"')[0]


            if (snode == node):
                if(type == 'type'):
                    link1.append(type + ": ")
                    page1.append(ename)
                else:
                    link1.append(type + ": ")
                    page1.append(ename)
            else:
                link2.append("->" + type + ":" + ename)
                page2.append(sname)
        # link1.sort()
        # link2.sort()
        # page1.sort()
        # page2.sort()
        if(link1 != [] and link2 != []):
            t1 = list(zip(link1, page1))
            t1.sort()
            link1[:], page1[:] = zip(*t1)
        if(link2 != [] and link2 != []):
            t2 = list(zip(page2, link2))
            t2.sort()
            page2[:], link2[:] = zip(*t2)
        link = link1 + link2
        page = page1 + page2
        leng = len(link1)

        return link, page, leng

    def getoutnode(graph, node):
        data = []
        rel = []
        edge = []
        if(graph.match_one(start_node=node, bidirectional=False)!=None):
            r = graph.match(start_node=node, bidirectional=False)
            for i in r:
                temp = str(i).split('-', 2)
                sid = temp[0].strip('()')
                eid = temp[2].strip('>()')
                type = i.type().split('_', 2)[2]
                edge = edge + [{"data": {'source': sid, 'target': eid, 'relationship': type}}]
                data.append(i.end_node())
                if i.type()=='ns1__type':
                    rel.append('type')
                elif i.type()=='ns1__sameAs':
                    rel.append('same')
                else:
                    rel.append('out')
        return data,rel,edge
        # cql = "match(n{ns0__label: '" + name + "'})-[r] - (m) return m"
        # res = graph.run(cql).data()
        # data = []
        # if res!=[]:
        #     for i in range(len(res)):
        #         data.append(res[i]['m'])
        # return data

    def getinnode(graph, node):
        data = []
        edge = []
        if(graph.match_one(end_node=node, bidirectional=False)!=None):
            rel = graph.match(end_node=node, bidirectional=False)
            for i in rel:
                temp = str(i).split('-', 2)
                sid = temp[0].strip('()')
                eid = temp[2].strip('>()')
                type = i.type().split('_', 2)[2]
                edge = edge + [{"data": {'source': sid, 'target': eid, 'relationship': type}}]
                data.append(i.start_node())
        return data,edge

        # cql = "match(m) - [r] - (n{ns0__label:'" + name + "'}) return m"
        # res = graph.run(cql).data()
        # data = []
        # if res!=[]:
        #     for i in range(len(res)):
        #         data.append(res[i]['m'])
        #return data

    def buildnode(node, type):
        temp = str(node).split(':',1)
        id = temp[0].lstrip('(')
        name = temp[1].split('/')[6].split('"')[0]
        data = {'id':id, 'name':name, 'type':type}
        return {"data":data}

    def asearch(graph,u1,u2):
        cql = "match p=allShortestPaths((n{uri:'" + u1 + "'})-[:ns2__症状相关症状|ns2__疾病相关疾病|ns2__症状相关疾病|ns2__疾病相关症状|ns2__检查相关疾病|ns2__疾病相关检查|ns2__检查相关症状|ns2__症状相关检查|ns2__症状相关药品|ns2__疾病相关药品|ns2__药品相关症状|ns2__药品相关疾病*0..5]-(m{uri:'" +u2 + "'})) return p"
        res = graph.run(cql).data()
        if(res):
            nodes = []
            ids = []
            outstr = ''
            path = res[0].get('p')
            print(path)
            for i in path.nodes():
                nodes.append(getnodename(i))
                ids.append(str(i).split(':')[0].strip('('))
            pathlen = len(path.relationships())
            pathstr = str(path).replace(':`ns2__','')
            pathstr = pathstr.replace('`','')
            print(pathstr)
            for i in range(len(nodes)):
                pathstr = pathstr.replace(ids[i],nodes[i])
            return nodes,pathstr
    # def buildedges(graph, node):
    #     relations = graph.match(start_node=node, bidirectional=True)
    #     data = []
    #     print(node)
    #     for i in relations:
    #         print(i)
    #         temp = str(i).split('-',2)
    #         sid = temp[0].strip('()')
    #         eid = temp[2].strip('>()')
    #         type = i.type().split('_', 2)[2]
    #         data = data + [{"data": {'source':sid, 'target':eid, 'relationship':type}}]
    #     return data

class Edit(Graph, NodeSelector, Node, Relationship):

    def relationadd(graph, startnode, relation, endnode): #input : URIs
        if Search.getnode(graph,startnode) == []:
            startnode = Node("Resource", ns0__label = (startnode.split('/',6))[6].split('"')[0], uri = startnode)
        else:
            startnode = Search.getnode(graph,startnode)
        #print(startnode)
        if Search.getnode(graph,endnode) == []:
            endnode = Node("Resource", ns0__label = (endnode.split('/',6))[6].split('"')[0], uri = endnode)
        else:
            endnode = Search.getnode(graph, endnode)
        #print(endnode)
        rel = Relationship(startnode, relation, endnode)
        #print(rel)
        s = startnode | endnode | rel
        graph.create(s)
        return rel

    def relationdelete(graph, selector, sname, rel, ename):
        #snode = graph.find_one(ns0__label=sname)
        #enode = graph.find_one(ns0__label=ename)
        # snode = selector.select("Resource", ns0__label=sname).first()
        # enode = selector.select("Resource", ns0__label=ename).first()
        # print(snode)
        # print(enode)
        rel = 'ns2__' + rel
        # relation = graph.match_one(start_node=snode, rel_type=rel, end_node=enode)
        # return graph.delete(relation)
        cql = "match (n{ns0__label:'" + sname + "'})-[r:" + rel + "]-(m{ns0__label:'" + ename + "'}) delete r"
        graph.run(cql)

    def nodedelete(graph, node):
        #need to delete all relation linked to node/subgraph
        #no api now/no need to do this
        return

    def relationedit(graph, startnode, relation, endnode):
        startnode = name2uri(startnode)
        endnode = name2uri(endnode)
        if Search.getnode(graph,startnode) == []:
            print('case1')
            startnode = Node("Resource", ns0__label = (startnode.split('/',6))[6].split('"')[0], uri = startnode)
            graph.create(startnode)
            print(startnode)
        else:
            startnode = Search.getnode(graph,startnode)
        if Search.getnode(graph,endnode) == []:
            endnode = Node("Resource", ns0__label = (endnode.split('/',6))[6].split('"')[0], uri = endnode)
            graph.create(endnode)
            print(startnode)
        else:
            endnode = Search.getnode(graph, endnode)
        chkexist = graph.match_one(start_node=startnode,end_node=endnode)
        if(chkexist!=None):
            chkrel = graph.match(start_node=startnode,end_node=endnode)
            for i in chkrel:
                type = i.type().split('_', 2)[2]
                if(type == relation):
                    #error
                    print('error')
                    return
        relation = 'ns2__' + relation
        Edit.relationadd(graph,startnode['uri'], relation, endnode['uri'])


        #or start from the node?


        # seq = "MATCH (n{uri:'" + URI + "'}) return n"
        # res = graph.run(seq).data()
        # #print(res) #list
        # #res[0] dict
        # #print(type(res[0].get('n'))) node
        # node = res[0].get('n')
        # #raw = node['uri']
        # #raw = raw.split('/',6)  #magic number,need to be edited
        # #result = (raw[6].split('"')[0])
        # result = Stext
        # #node = Resource.select(graph).where(uri=URI).first()
        # #print(type(node))
        #
        # #need to do : resolve relationships
        # relations = graph.match(start_node = node, bidirectional=True)
        # link = []
        # for i in relations:
        #     type = i.type.split('_',2)[2]
        #     snode = i.start_node()
        #     enode = i.end_node()
        #     sname = (snode['uri'].split('/',6))[6].split('"')[0]
        #     ename = (enode['uri'].split('/',6))[6].split('"')[0]
        #
        #     if(snode == node):
        #         link.append(type + ": " + ename)
        #     else:
        #         link.append(ename + "->" + sname)