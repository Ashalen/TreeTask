"""
Main entry point for the TreeTask Flask application.
"""
from flask import Flask
from flask_login import LoginManager
from controllers.auth_controller import auth_bp
from controllers.task_controller import task_bp
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(task_bp)

# User loader for Flask-Login
from models.user import User
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Ensure instance folder exists
os.makedirs(os.path.join(app.instance_path), exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True)
