#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 20:54

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import render_template
from . import main

@main.route('/')
def index():
    return render_template('index.html')


