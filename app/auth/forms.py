#!/usr/bin/env
# coding:utf-8
"""
Created on 27/07/2016 22:03

__author__ = 'Yang'
__version__= '1.0'

"""

from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Email

class LoginForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
