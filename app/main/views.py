#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 20:54

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import render_template,abort,redirect,url_for,flash
from flask.ext.login import current_user,login_required
from . import main
from ..models import User
from .forms import EditProfile
from .. import db

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('main.user',username=current_user.username))
    #to load data from db and shown on page
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)


@main.route('/about')
def about():
    return render_template('about.html')