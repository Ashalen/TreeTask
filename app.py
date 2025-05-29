"""
Main entry point for the TreeTask Flask application.
"""
from flask import Flask
from flask_login import LoginManager
from controllers.auth_controller import auth_bp
from controllers.task_controller import task_bp
from config import Config
import os
from werkzeug.security import generate_password_hash
from models.user import User

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
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

def create_default_demo_user():
    from models.db import get_db
    db = get_db()
    username = "Demo"
    password = "Demo@12345"
    password_hash = generate_password_hash(password)
    # Check if user already exists
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if not user:
        db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        db.commit()
        print("Default demo user created: Demo / Demo@12345")
    else:
        print("Demo user already exists.")

# Ensure instance folder exists
os.makedirs(os.path.join(app.instance_path), exist_ok=True)

if __name__ == '__main__':
    with app.app_context():
        create_default_demo_user()
    app.run(debug=True)
