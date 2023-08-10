import sqlite3
import os


from .import DB_NAME
from . import engine

from src.models import Word, Pending


def create_api_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL UNIQUE,
            count INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def create_api_records():
    apis = ["writing/Generate Topic", "writing/Grade Writing", "writing/Check Grammar", "writing/Rewrite Writing", "writing/Write Essay"]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for api in apis:
        c.execute("INSERT OR IGNORE INTO api_records (endpoint) VALUES (?)", (api, ))

    conn.commit()
    conn.close()


def increment_api_count(endpoint):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE api_records SET count = count + 1 WHERE endpoint = ?", (endpoint, ))
    conn.commit()
    conn.close()


def get_writing_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM api_records WHERE endpoint LIKE 'writing/%'")
    rows = c.fetchall()
    conn.close()
    return rows


def create_tables():
    Word.__table__.create(bind=engine, checkfirst=True)
    Pending.__table__.create(bind=engine, checkfirst=True)
    create_api_table()
    create_api_records()
