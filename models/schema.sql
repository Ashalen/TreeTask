-- SQL schema for TreeTask

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    creation_date TEXT NOT NULL,
    due_date TEXT, -- ISO 8601 string, nullable
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
