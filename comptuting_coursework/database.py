import sqlite3
from flask import g

DATABASE = 'stride.db'

def get_db():
    """Get database connection for current request"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with schema"""
    db = get_db()
    
    # Create tasks table
    db.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            status TEXT DEFAULT 'Not Started',
            due_date DATE,
            priority TEXT DEFAULT 'Medium',
            time_needed REAL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create settings table
    db.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            study_start_time TIME DEFAULT '09:00',
            study_end_time TIME DEFAULT '17:00',
            excluded_days TEXT DEFAULT ''
        )
    ''')
    
    # Insert default settings if not exists
    existing = db.execute('SELECT id FROM settings WHERE id = 1').fetchone()
    if not existing:
        db.execute('''
            INSERT INTO settings (id, study_start_time, study_end_time, excluded_days)
            VALUES (1, '09:00', '17:00', '')
        ''')
    
    db.commit()
