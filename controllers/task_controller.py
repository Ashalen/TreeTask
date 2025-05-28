"""
Task controller: handles dashboard and task CRUD routes, plus REST API endpoint.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.task import Task
from models.db import get_db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional
from markupsafe import escape
from datetime import datetime

# Blueprint for task management
task_bp = Blueprint('task', __name__)

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    due_time = StringField('Due Time (optional)', validators=[Optional(), Length(max=5)])  # HH:MM
    submit = SubmitField('Add Task')

class EditTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    due_time = StringField('Due Time (optional)', validators=[Optional(), Length(max=5)])
    submit = SubmitField('Update Task')

@task_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TaskForm()
    search_query = request.args.get('q', '').strip() if request.method == 'GET' else ''
    if request.method == 'POST':
        if form.validate_on_submit():
            safe_title = escape(form.title.data)
            safe_description = escape(form.description.data)
            due_date = form.due_date.data
            due_time = form.due_time.data.strip() if form.due_time.data else ''
            due_datetime = None
            if due_date:
                if due_time:
                    try:
                        due_datetime = f"{due_date.isoformat()}T{due_time}:00"
                    except Exception:
                        due_datetime = due_date.isoformat()
                else:
                    due_datetime = due_date.isoformat()
            Task.create(current_user.id, safe_title, safe_description, due_datetime)
            flash('Task added!', 'success')
            return redirect(url_for('task.dashboard'))
        else:
            flash('Error adding task.', 'error')
    if search_query:
        tasks = Task.search_by_user(current_user.id, search_query)
    else:
        tasks = Task.get_all_by_user(current_user.id)
    now_str = datetime.utcnow().isoformat(timespec='minutes')
    return render_template('dashboard.html', tasks=tasks, form=form, search_query=search_query, now=now_str)

@task_bp.route('/add', methods=['POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        safe_title = escape(form.title.data)
        safe_description = escape(form.description.data)
        due_date = form.due_date.data
        due_time = form.due_time.data.strip() if form.due_time.data else ''
        due_datetime = None
        if due_date:
            if due_time:
                try:
                    due_datetime = f"{due_date.isoformat()}T{due_time}:00"
                except Exception:
                    due_datetime = due_date.isoformat()
            else:
                due_datetime = due_date.isoformat()
        Task.create(current_user.id, safe_title, safe_description, due_datetime)
        flash('Task added!', 'success')
    else:
        flash('Error adding task.', 'error')
    return redirect(url_for('task.dashboard'))

@task_bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    Task.delete(task_id, current_user.id)
    flash('Task deleted.', 'success')
    return redirect(url_for('task.dashboard'))

@task_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.get_by_id(task_id, current_user.id)
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('task.dashboard'))
    # Pre-fill due_date and due_time for the form
    from datetime import datetime
    due_date_val = None
    due_time_val = ''
    if task.due_date:
        try:
            dt = datetime.fromisoformat(task.due_date)
            due_date_val = dt.date()
            due_time_val = dt.strftime('%H:%M') if dt.hour or dt.minute else ''
        except Exception:
            pass
    form = EditTaskForm(obj=task)
    if request.method == 'GET':
        form.due_date.data = due_date_val
        form.due_time.data = due_time_val
    if form.validate_on_submit():
        safe_title = escape(form.title.data)
        safe_description = escape(form.description.data)
        due_date = form.due_date.data
        due_time = form.due_time.data.strip() if form.due_time.data else ''
        due_datetime = None
        if due_date:
            if due_time:
                try:
                    due_datetime = f"{due_date.isoformat()}T{due_time}:00"
                except Exception:
                    due_datetime = due_date.isoformat()
            else:
                due_datetime = due_date.isoformat()
        Task.update(task_id, current_user.id, safe_title, safe_description, due_datetime)
        flash('Task updated!', 'success')
        return redirect(url_for('task.dashboard'))
    return render_template('edit_task.html', form=form, task=task)

# REST API endpoint for tasks
@task_bp.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    if request.method == 'GET':
        tasks = Task.get_all_by_user(current_user.id)
        return jsonify([task.to_dict() for task in tasks])
    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        Task.create(current_user.id, title, description)
        return jsonify({'message': 'Task created'}), 201

@task_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')

@task_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    from models.user import User
    User.delete(current_user.id)
    from flask_login import logout_user
    logout_user()
    from flask import flash, redirect, url_for
    flash('Your account and all associated tasks have been deleted.', 'success')
    return redirect(url_for('auth.login'))
