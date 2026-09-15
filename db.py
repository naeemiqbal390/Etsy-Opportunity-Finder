"""
db.py — SQLite persistence for saved opportunities.
No API key needed — this is a local file-based database.

NOTE: On free hosts like Streamlit Community Cloud the filesystem is
ephemeral: radar_database.db will survive while the app stays awake, but
it can be wiped on a redeploy, a sleep/wake cycle, or a restart. Use the
CSV download button in app.py to back up your data regularly if you rely
on free hosting long-term.
"""

import sqlite3
import json

DB_FILE = "radar_database.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def save_opportunity(record: dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO opportunities (product, data) VALUES (?, ?)",
        (record["idea"]["product"], json.dumps(record)),
    )
    conn.commit()
    conn.close()


def load_opportunities() -> list:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM opportunities ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]
