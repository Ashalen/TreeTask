"""
Database connection and initialization utilities for TreeTask.
"""
import sqlite3
from flask import g
from config import Config
import os

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(Config.DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(Config.DB_PATH)
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
        db.executescript(f.read())
    db.close()
