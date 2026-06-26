import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'database.db'

ACTIVITY_POINTS = {
    'recycled_waste': 5,
    'public_transportation': 4,
    'bicycle': 4,
    'planted_tree': 10,
    'saved_electricity': 3,
    'saved_water': 3
}

ACTIVITY_NAMES = {
    'recycled_waste': 'Recycled Waste',
    'public_transportation': 'Used Public Transportation',
    'bicycle': 'Rode a Bicycle',
    'planted_tree': 'Planted a Tree',
    'saved_electricity': 'Saved Electricity',
    'saved_water': 'Saved Water'
}


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not os.path.exists(DATABASE_PATH):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT,
                points INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()


def create_user(username, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
        (username, email, password_hash)
    )
    
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    return user_id


def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user


def add_activity(user_id, activity_type, description=''):
    points = ACTIVITY_POINTS.get(activity_type, 0)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO activities (user_id, activity_type, description, points) VALUES (?, ?, ?, ?)',
        (user_id, activity_type, description, points)
    )
    
    conn.commit()
    activity_id = cursor.lastrowid
    conn.close()
    
    return activity_id


def get_user_activities(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM activities WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    )
    activities = cursor.fetchall()
    
    conn.close()
    return activities


def get_activity_by_id(activity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM activities WHERE id = ?', (activity_id,))
    activity = cursor.fetchone()
    
    conn.close()
    return activity


def update_activity(activity_id, activity_type, description=''):
    points = ACTIVITY_POINTS.get(activity_type, 0)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE activities SET activity_type = ?, description = ?, points = ? WHERE id = ?',
        (activity_type, description, points, activity_id)
    )
    
    conn.commit()
    conn.close()


def delete_activity(activity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM activities WHERE id = ?', (activity_id,))
    
    conn.commit()
    conn.close()


def get_user_total_points(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(points) as total FROM activities WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    return result['total'] or 0


def get_user_activity_count(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM activities WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    return result['count']


def get_user_most_common_activity(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT activity_type, COUNT(*) as count 
        FROM activities 
        WHERE user_id = ? 
        GROUP BY activity_type 
        ORDER BY count DESC 
        LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return ACTIVITY_NAMES.get(result['activity_type'], result['activity_type'])
    
    return None


def get_activity_display_name(activity_type):
    return ACTIVITY_NAMES.get(activity_type, activity_type)