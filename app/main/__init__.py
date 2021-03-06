#!/usr/bin/env
# coding:utf-8
"""
Created on 18/07/2016 22:25

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
