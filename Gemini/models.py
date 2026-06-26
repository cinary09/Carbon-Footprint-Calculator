import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            points INTEGER NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username, password):
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return user
    return None

def add_activity(user_id, activity_type, points, description):
    conn = get_db_connection()
    conn.execute('INSERT INTO activities (user_id, activity_type, points, description) VALUES (?, ?, ?, ?)',
                 (user_id, activity_type, points, description))
    conn.commit()
    conn.close()

def get_user_activities(user_id):
    conn = get_db_connection()
    activities = conn.execute('SELECT * FROM activities WHERE user_id = ? ORDER BY timestamp DESC', (user_id,)).fetchall()
    conn.close()
    return activities

def get_activity(activity_id, user_id):
    conn = get_db_connection()
    activity = conn.execute('SELECT * FROM activities WHERE id = ? AND user_id = ?', (activity_id, user_id)).fetchone()
    conn.close()
    return activity

def update_activity(activity_id, user_id, activity_type, points, description):
    conn = get_db_connection()
    conn.execute('UPDATE activities SET activity_type = ?, points = ?, description = ? WHERE id = ? AND user_id = ?',
                 (activity_type, points, description, activity_id, user_id))
    conn.commit()
    conn.close()

def delete_activity(activity_id, user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM activities WHERE id = ? AND user_id = ?', (activity_id, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = get_db_connection()
    total_activities = conn.execute('SELECT COUNT(*) FROM activities WHERE user_id = ?', (user_id,)).fetchone()[0]
    total_points = conn.execute('SELECT SUM(points) FROM activities WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
    
    most_common_row = conn.execute('''
        SELECT activity_type, COUNT(activity_type) as qty 
        FROM activities 
        WHERE user_id = ? 
        GROUP BY activity_type 
        ORDER BY qty DESC 
        LIMIT 1
    ''', (user_id,)).fetchone()
    
    most_common_activity = most_common_row['activity_type'] if most_common_row else "None"
    conn.close()
    
    return {
        'total_activities': total_activities,
        'total_points': total_points,
        'most_common_activity': most_common_activity
    }