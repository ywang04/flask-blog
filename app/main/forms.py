#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 21:34

__author__ = 'Yang'
__version__= '1.0'

"""

from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField,ValidationError
from wtforms.validators import Required,Length,Email,Regexp
from ..models import Role,User,Category
from flaskckeditor import CKEditor

class EditProfile(Form):
    #db has the length limit
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),
                                            Email()])
    username = StringField('Username',validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])

    confirmed = BooleanField('Confirmed')
    #SelectField is a dropdown list in the form
    role = SelectField('Role',coerce=int)
    name = StringField('Real name', validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        #choices is the role's attribute while role is the instance of SelectField
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
            User.query.filter_by(email= field.data).first():
            raise ValidationError('Email already registered.')


    def validate_username(self,field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form,CKEditor):
    title = StringField('Enter Title',validators=[Required()])
    category = SelectField('Select Category',coerce=int)
    body = TextAreaField("What's on your mind?",validators=[Required()])
    submit = SubmitField('Post')

    def __init__(self,*args,**kwargs):
        super(PostForm,self).__init__(*args,**kwargs)
        #choices is the category's attribute while category is the instance of SelectField
        self.category.choices = [(category.id,category.category_name)
                                 for category in Category.query.order_by(Category.category_name).all()]

class CommentForm(Form):
    body = StringField('Add a comment',validators=[Required()])
    submit = SubmitField('Comment')


class AddCategory(Form):
    category = StringField('Please enter category name',validators=[Required(),Length(0,128)])
    submit = SubmitField('Create Category')





