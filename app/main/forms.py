#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 21:34

__author__ = 'Yang'
__version__= '1.0'

"""

from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required

class NameForm(Form):
    name = StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')