#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 20:54

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

