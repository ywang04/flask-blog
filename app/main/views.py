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
from ..models import User,Role,Permission,Post,Category,Comment,Like
from .forms import EditProfile,EditProfileAdminForm,PostForm,AddCategory,CommentForm
from .. import db
from ..decorators import admin_required,permission_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from ..auth.forms import ChangeProfileForm

@main.route('/',methods=['GET','POST'])
def index():
    #http://localhost:5000/?page=2,to get the value of page, which is 2
    page = request.args.get('page',1,type=int)
    show_followed = False
    # post_top = True
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

    categories = Category.query.order_by(Category.category_name).all()
    return render_template('index.html',posts=posts,show_followed=show_followed,pagination=pagination,
                           categories=categories,Post=Post)

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

@main.route('/profile-edit',methods=['GET','POST'])
@login_required
def profile_edit():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user',username=current_user.username))
    #to load data from db and shown on page
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('profile_edit.html',form=form)



@main.route('/profile-edit/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def profile_edit_admin(id):
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
        db.session.commit()
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
    return render_template('profile_edit.html',form=form,user=user)

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
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

@main.route('/post-new/',methods=['GET','POST'])
@login_required
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        #category is an object(<app.models.Category object at 0x10faded90>)
        post = Post(title=form.title.data,category=Category.query.get(form.category.data),body=form.body.data,
                    author=current_user._get_current_object())
        res = Like(post=post, user=current_user._get_current_object(), liked=False)
        db.session.add(post,res)
        db.session.commit()
        flash('Your post has been published.')
        return redirect(url_for('main.post',id=post.id))
    return render_template('post_new.html',form=form)

@main.route('/post-edit/<int:id>',methods=['GET','POST'])
@login_required
def post_edit(id):
    #check the id and permission for the post
    post = Post.query.get_or_404(id)
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
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('main.post',id=post.id))
    form.title.data = post.title
    form.category.data = post.category_id
    form.body.data = post.body
    return render_template('post_edit.html',form=form,post=post)

@main.route('/post-delete/<int:id>',methods=['GET','POST'])
@login_required
def post_delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
          not current_user.is_administrator:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return 'post deleted.'


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
@login_required
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
@login_required
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

#CKEDITOR function
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

@main.route('/post-category/<int:id>')
def post_category(id):
    #difference between filter and filter_by,both are fine.
    # posts = Post.query.filter(Post.category_id==id)
    page = request.args.get('page', 1, type=int)
    post = Post.query.filter_by(category_id=id)
    categories = Category.query.order_by(Category.category_name).all()
    pagination = post.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['YUORA_POSTS_PER_PAGE'],error_out=False)
    posts = pagination.items
    return render_template('post_category.html',posts=posts,categories=categories,Post=Post,category_id=id,
                           pagination = pagination)


@main.route('/category/top/<int:id>')
def category_top(id):
    page = request.args.get('page', 1, type=int)
    query = Post.query.filter_by(category_id=id).join(Like, Like.post_id == Post.id).add_columns(func.sum(Like.liked)).group_by(Post.id).order_by(
        func.sum(Like.liked).desc())
    print query
    pagination = query.paginate(
        page, per_page=current_app.config['YUORA_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    categories = Category.query.order_by(Category.category_name).all()
    return render_template('category_top.html', posts=posts, pagination=pagination,
                           categories=categories, Post=Post,category_id=id)

@main.route('/post/like/<int:id>',methods=['GET','POST'])
@login_required
def post_like(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        if current_user.is_like_post(post):
            res = Like.query.filter_by(post_id=post.id).filter_by(user_id = current_user.id).first()
            if res:
                res.liked = False
                db.session.add(res)
        else:
            res = Like.query.filter_by(post_id=post.id).filter_by(user_id = current_user.id).first()
            if res:
                res.liked = True
                db.session.add(res)
            else:
                res = Like(post=post, user=current_user._get_current_object(),liked=True)
                db.session.add(res)
        db.session.commit()
        return '{"status": "ok"}'
    # return redirect(url_for('main.index'))


@main.route('/post/top')
def post_top():
    page = request.args.get('page', 1, type=int)

#select * from posts ps join (SELECT ls.post_id,count(ls.post_id) as c FROM likes ls GROUP BY ls.post_id) ls on ps.id = ls.post_id order by c desc;
    query = Post.query.join(Like,Like.post_id==Post.id).add_columns(func.sum(Like.liked)).group_by(Post.id).order_by(func.sum(Like.liked).desc())
    print query
    pagination = query.paginate(
    page, per_page=current_app.config['YUORA_POSTS_PER_PAGE'],
    error_out=False)
    posts = pagination.items
    categories = Category.query.order_by(Category.category_name).all()
    return render_template('post_all_top.html', posts=posts, pagination=pagination,
                           categories=categories, Post=Post)


@main.route('/category-add',methods=['GET','POST'])
@admin_required
def category_add():
    form = AddCategory()
    if form.validate_on_submit():
        category = Category(category_name=form.category.data)
        try:
            db.session.add(category)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash('%s already exists.' % category.category_name )
            return redirect(url_for('main.category_add'))
        flash('%s has been added.' % category.category_name)
        return redirect(url_for('main.category_add'))
    categories = Category.query.order_by(Category.category_name).all()
    return render_template('category_add.html',form=form,categories=categories)


@main.route('/settings/<username>',methods=['GET','POST'])
@login_required
def settings(username):
    form = ChangeProfileForm()
    if form.validate_on_submit():
        # if current_user.verify_password(form.old_password.data):
        #     current_user.password = form.password.data
        #     db.session.add(current_user)
        #     flash('Your profile has been updated.')
        #     return redirect(url_for('main.settings',username=current_user.username))
        # else:
        #     flash('Old password is wrong. Please try again.')
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('settings.html',form=form,user=current_user._get_current_object())


@main.route('/about')
def about():
    return render_template('about.html')



