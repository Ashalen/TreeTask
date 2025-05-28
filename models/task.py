"""
Task model for TreeTask, using direct sqlite3 access.
"""
from models.db import get_db
from datetime import datetime

class Task:
    def __init__(self, id, user_id, title, description, creation_date, due_date=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.creation_date = creation_date
        self.due_date = due_date

    @staticmethod
    def create(user_id, title, description, due_date=None):
        db = get_db()
        db.execute(
            'INSERT INTO tasks (user_id, title, description, creation_date, due_date) VALUES (?, ?, ?, ?, ?)',
            (user_id, title, description, datetime.utcnow(), due_date)
        )
        db.commit()

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        rows = db.execute(
            'SELECT * FROM tasks WHERE user_id = ? ORDER BY \
                CASE WHEN due_date IS NOT NULL THEN due_date ELSE creation_date END ASC',
            (user_id,)).fetchall()
        return [Task(row['id'], row['user_id'], row['title'], row['description'], row['creation_date'], row['due_date']) for row in rows]

    @staticmethod
    def get_by_id(task_id, user_id):
        db = get_db()
        row = db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
        if row:
            return Task(row['id'], row['user_id'], row['title'], row['description'], row['creation_date'], row['due_date'])
        return None

    @staticmethod
    def update(task_id, user_id, title, description, due_date=None):
        db = get_db()
        db.execute('UPDATE tasks SET title = ?, description = ?, due_date = ? WHERE id = ? AND user_id = ?', (title, description, due_date, task_id, user_id))
        db.commit()

    @staticmethod
    def delete(task_id, user_id):
        db = get_db()
        db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        db.commit()

    @staticmethod
    def search_by_user(user_id, query):
        db = get_db()
        like_query = f"%{query}%"
        rows = db.execute(
            'SELECT * FROM tasks WHERE user_id = ? AND (title LIKE ? OR description LIKE ?) ORDER BY \
                CASE WHEN due_date IS NOT NULL THEN due_date ELSE creation_date END ASC',
            (user_id, like_query, like_query)
        ).fetchall()
        return [Task(row['id'], row['user_id'], row['title'], row['description'], row['creation_date'], row['due_date']) for row in rows]

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date,
            'due_date': self.due_date
        }
