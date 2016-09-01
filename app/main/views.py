#!/usr/bin/env
# coding:utf-8
"""
Created on 19/07/2016 20:54

__author__ = 'Yang'
__version__= '1.0'

"""

import os,random,datetime
from flask import render_template,abort,redirect,url_for,flash,request,current_app,make_response
from flask.ext.login import current_user,login_required
from . import main
from ..models import User,Role,Permission,Post,Category,Comment
from .forms import EditProfile,EditProfileAdminForm,PostForm,AddCategory,CommentForm
from .. import db
from ..decorators import admin_required,permission_required
from sqlalchemy.exc import IntegrityError

@main.route('/',methods=['GET','POST'])
def index():
    #http://localhost:5000/?page=2,to get the value of page, which is 2
    page = request.args.get('page',1,type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    #pagination is a <flask_sqlalchemy.Pagination object at 0x10e50cf10> object, class Pagination

    pagination = query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['YUORA_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html',posts=posts,show_followed=show_followed,pagination=pagination)


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
        (page,per_page=current_app.config['YUORA_POSTS_PER_PAGE'],
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

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('main.post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['YUORA_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page= current_app.config['YUORA_COMMENTS_PER_PAGE'],
        error_out = False)
    comments = pagination.items
    return render_template('post.html',post=post,form=form,comments=comments,pagination=pagination)

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
    return render_template('edit_post.html',form=form,post=post)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.user',username=username))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    flash('You are now following {}.'.format(username))
    return redirect(url_for('main.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.user',username=username))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('main.user',username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.user',username=username))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page,per_page=current_app.config['YUORA_FOLLOWERS_PER_PAGE'],
        error_out = False)
    follows = [{'user':item.follower,'timestamp': item.timestamp} for item in pagination.items]
    #[{'timestamp': datetime.datetime(2016, 8, 29, 5, 55, 21), 'user': <User u'Admin'>}, {'timestamp': datetime.datetime(2016, 8, 30, 6, 3, 55), 'user': <User u'yang01'>}]
    return render_template('followers.html',user=user,title='Followers of',
                           endpoint='main.followers',pagination=pagination,
                           follows=follows)

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.user',username=username))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(
        page,per_page=current_app.config['YUORA_FOLLOWERS_PER_PAGE'],
        error_out = False)
    follows = [{'user':item.followed,'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followed by',
                           endpoint='main.followed_by', pagination=pagination,
                           follows=follows)

@main.route('/all')
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@main.route('/ckupload/', methods=['POST','GET'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'upload', rnd_name)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """<script type="text/javascript">
             window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
             </script>""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

@main.route('/add-Category',methods=['GET','POST'])
@admin_required
def add_category():
    form = AddCategory()
    if form.validate_on_submit():
        category = Category(category_name=form.category.data)
        try:
            db.session.add(category)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash('Category already exists.')
            return redirect(url_for('main.add_category'))
        flash('Category has been added.')
        return redirect(url_for('main.add_category'))

    categories = Category.query.order_by(Category.category_name).all()
    return render_template('add_category.html',form=form,categories=categories)

@main.route('/about')
def about():
    return render_template('about.html')



