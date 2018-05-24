from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired
from app.models import *

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit_btn = SubmitField('登录')
    regist_btn = SubmitField('注册')

class RegisterForm(FlaskForm):
    username=StringField('用户名',validators=[DataRequired()])
    password=PasswordField('密码',validators=[DataRequired()])
    submit=SubmitField('register')

class SearchForm(FlaskForm):
    context = StringField('搜索内容')
    submit_btn = SubmitField('GO!')
    add_btn = SubmitField('增加条目')

class ReturnForm(FlaskForm):
    return_btn = SubmitField('返回')
    edit_btn = SubmitField('编辑')

class ReturnForm1(FlaskForm):
    return_btn = SubmitField('返回')

class AddForm(FlaskForm):
    snode = StringField('Start Node', validators=[DataRequired()])
    relation = StringField('Relationship', validators=[DataRequired()])
    enode = StringField('End Node', validators=[DataRequired()])
    submit_btn = SubmitField('Submit')

class Advsearch(FlaskForm):
    node1 = StringField('Node1', validators=[DataRequired()])
    node2 = StringField('Node2', validators=[DataRequired()])
    submit_btn = SubmitField('Submit')