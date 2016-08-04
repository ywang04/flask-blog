#!/usr/bin/env
# coding:utf-8
"""
Created on 3/08/2016 09:38

__author__ = 'Yang'
__version__= '1.0'

"""

from functools import wraps
from flask import abort
from flask.ext.login import current_user
from models import Permission

def permission_required(permission):
    def decorator(f):
        #functools
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

