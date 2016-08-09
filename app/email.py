#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 11:53

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import current_app,render_template
from threading import Thread
from flask.ext.mail import Message
from . import mail


def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(to,subject,template,**kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['YBLOG_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender = app.config['YBLOG_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
