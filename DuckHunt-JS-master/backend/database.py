import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'scores.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    # Create table with phone column (new installs)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            phone      TEXT    NOT NULL DEFAULT '',
            score      INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safe migration: add phone column if it doesn't exist yet
    existing = {row[1] for row in conn.execute("PRAGMA table_info(scores)")}
    if 'phone' not in existing:
        conn.execute("ALTER TABLE scores ADD COLUMN phone TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()
