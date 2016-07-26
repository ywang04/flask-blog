#!/usr/bin/env
# coding:utf-8
"""
Created on 26/07/2016 20:41

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views