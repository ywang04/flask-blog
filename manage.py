#!/usr/bin/env
# coding:utf-8
"""
Created on 20/07/2016 16:06

__author__ = 'Yang'
__version__= '1.0'

"""

#! /usr/bin/env python
import os
from app import create_app,db
from app.models import User,Role
from flask.ext.script import Manager,Shell
from flask.ext.migrate import Migrate,MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
