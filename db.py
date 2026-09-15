"""
db.py — SQLite persistence for saved opportunities.
"""

import sqlite3
import json

DB_FILE = "radar_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_opportunity(record: dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO opportunities (product, data) VALUES (?, ?)", 
              (record["idea"]["product"], json.dumps(record)))
    conn.commit()
    conn.close()

def load_opportunities() -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM opportunities ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]
