"""
Authentication controller: handles login, logout, and registration routes.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from models.db import get_db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from markupsafe import escape
import re

# Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

def strong_password(form, field):
    password = field.data or ''
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    # Special characters: @ _ - .
    if not re.search(r'^[A-Za-z0-9@_.-]+$', password):
        raise ValidationError('Password can only contain letters, numbers, and these special characters: @ _ - .')
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        raise ValidationError('Password must include both a letter and a number.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), strong_password])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        safe_username = escape(form.username.data)
        user = User.get_by_username(safe_username)
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('task.dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('task.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        safe_username = escape(form.username.data)
        if User.get_by_username(safe_username):
            flash('Username already exists', 'error')
        else:
            try:
                password_hash = generate_password_hash(form.password.data)
                User.create(safe_username, password_hash)
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash('An error occurred during registration. Please try again.', 'error')
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
