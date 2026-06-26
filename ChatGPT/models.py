import sqlite3
from dataclasses import dataclass
from pathlib import Path
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    points INTEGER NOT NULL,
    activity_date TEXT NOT NULL,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""


def get_db_path():
    return str(DB_PATH)


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as connection:
        connection.executescript(SCHEMA)


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    created_at: str

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@dataclass
class Activity:
    id: int
    user_id: int
    activity_type: str
    points: int
    activity_date: str
    notes: str
    created_at: str


def row_to_user(row):
    if row is None:
        return None
    return User(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
    )


def row_to_activity(row):
    if row is None:
        return None
    return Activity(
        id=row["id"],
        user_id=row["user_id"],
        activity_type=row["activity_type"],
        points=row["points"],
        activity_date=row["activity_date"],
        notes=row["notes"] or "",
        created_at=row["created_at"],
    )


def get_user_by_username(username):
    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    return row_to_user(row)


def get_user_by_id(user_id):
    if user_id is None:
        return None
    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return row_to_user(row)


def create_user(username, password):
    password_hash = generate_password_hash(password)
    with get_db_connection() as connection:
        connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        connection.commit()


def create_activity(user_id, activity_type, points, activity_date, notes):
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO activities (user_id, activity_type, points, activity_date, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, activity_type, points, activity_date, notes),
        )
        connection.commit()


def get_user_activities(user_id):
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM activities
            WHERE user_id = ?
            ORDER BY activity_date DESC, created_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
    return [row_to_activity(row) for row in rows]


def get_activity_by_id(activity_id):
    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT * FROM activities WHERE id = ?",
            (activity_id,),
        ).fetchone()
    return row_to_activity(row)


def update_activity(activity_id, activity_type, points, activity_date, notes):
    with get_db_connection() as connection:
        connection.execute(
            """
            UPDATE activities
            SET activity_type = ?, points = ?, activity_date = ?, notes = ?
            WHERE id = ?
            """,
            (activity_type, points, activity_date, notes, activity_id),
        )
        connection.commit()


def delete_activity(activity_id):
    with get_db_connection() as connection:
        connection.execute(
            "DELETE FROM activities WHERE id = ?",
            (activity_id,),
        )
        connection.commit()


def get_user_statistics(user_id):
    with get_db_connection() as connection:
        totals = connection.execute(
            """
            SELECT COUNT(*) AS total_activities, COALESCE(SUM(points), 0) AS total_points
            FROM activities
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        common = connection.execute(
            """
            SELECT activity_type, COUNT(*) AS activity_count
            FROM activities
            WHERE user_id = ?
            GROUP BY activity_type
            ORDER BY activity_count DESC, activity_type ASC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return {
        "total_activities": totals["total_activities"],
        "total_points": totals["total_points"],
        "most_common_activity": common["activity_type"] if common else "No activities yet",
    }
