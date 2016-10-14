#!/usr/bin/env
# coding:utf-8
"""
Created on 27/07/2016 22:03

__author__ = 'Yang'
__version__= '1.0'

"""

from flask.ext.wtf import Form
# from flask.ext.uploads import UploadSet, IMAGES
# from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import Required,Email,Length,Regexp,EqualTo,DataRequired
from wtforms import ValidationError
from ..models import User

# images = UploadSet('images', IMAGES)

class LoginForm(Form):
    email = StringField('Email address',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Stay signed in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email address',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('Username',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                                                 'Usernames must have only letters, '
                                                                                 'numbers, dots or underscores')])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Passwords must match.')])
    password2 = PasswordField('Re-enter password',validators=[DataRequired()])
    submit = SubmitField('Sign Up Now',render_kw={"class":"btn btn-primary btn-block"})


    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangeProfileForm(Form):
    name = StringField('Real name',render_kw={'cols':'700px','rows':'500px'},validators=[DataRequired(), Length(0, 64)],)
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Update Profile',render_kw={'class': "btn btn-primary btn-block"})


class PasswordResetRequestForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    submit = SubmitField('Reset Password')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class PasswordResetForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old_password',validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(),EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

# class PhotoForm(Form):
#     photo = FileField('Image', validators=[
#         FileRequired(),
#         FileAllowed(images, 'Images only!')
#     ])
#
#     # photo = FileField('Your photo')
#     submit = SubmitField('Update Image')