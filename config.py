"""
Configuration for the TreeTask Flask application.
"""
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DB_PATH = os.path.join(os.path.dirname(__file__), 'treetask.db')
    WTF_CSRF_ENABLED = True
