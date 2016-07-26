#!/usr/bin/env
# coding:utf-8
"""
Created on 26/07/2016 20:42

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import render_template
from . import auth

@auth.route('/login')
def login():
    return render_template('auth/login.html')

