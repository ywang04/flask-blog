#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 20:54

__author__ = 'Yang'
__version__= '1.0'

"""

from flask import render_template,abort,redirect,url_for,flash,request,current_app
from flask.ext.login import current_user,login_required
from . import main
from ..models import User,Role,Permission,Post,Category
from .forms import EditProfile,EditProfileAdminForm,PostForm,AddCategory
from .. import db
from ..decorators import admin_required

@main.route('/',methods=['GET','POST'])
def index():
    #http://localhost:5000/?page=2,to get the value of page, which is 2
    page = request.args.get('page',1,type=int)

    #pagination is a <flask_sqlalchemy.Pagination object at 0x10e50cf10> object, class Pagination

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['YBLOG_POSTS_PER_PAGE'],
            error_out=False)

    posts = pagination.items
    return render_template('index.html',posts=posts,pagination=pagination)


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    #The list of blog posts for a user is obtained from the User.posts relationship,
    # which is a query object, so filters such as order_by() can be used on it as well.
    page = request.args.get('page',1,type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate\
        (page,per_page=current_app.config['YBLOG_POSTS_PER_PAGE'],
         error_out = False)
    posts = pagination.items
    return render_template('homepage.html',user=user,posts=posts,pagination=pagination)

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


@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('main.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    #should be role_id instead of role
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',post=post)

@main.route('/new-post',methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        #category is an object(<app.models.Category object at 0x10faded90>)
        post = Post(title=form.title.data,category=Category.query.get(form.category.data),body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('Your post has been published.')
        return redirect(url_for('main.post',id=post.id))
    return render_template('new_post.html',form=form)

@main.route('/edit-post/<int:id>',methods=['GET','POST'])
def edit_post(id):
    #check the id and permission for the post
    post = Post.query.get_or_404(id)
    # if current_user != post.author and \
    #     not current_user.is_administrator:
    #     abort(403)
    if current_user != post.author and \
          not current_user.is_administrator:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #form.category.data is to get the category id in categories table
        #Category.query.get(id) is to get the category object
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('main.post',id=post.id))
    form.title.data = post.title
    form.category.data = post.category_id
    form.body.data = post.body
    return render_template('edit_post.html',form=form)





@main.route('/add-Category',methods=['GET','POST'])
@admin_required
def add_category():
    form = AddCategory()
    if form.validate_on_submit():
        category = Category(category_name=form.category.data)
        db.session.add(category)
        return redirect(url_for('main.add_category'))
    categories = Category.query.order_by(Category.category_name).all()
    return render_template('add_category.html',form=form,categories=categories)

@main.route('/about')
def about():
    return render_template('about.html')



