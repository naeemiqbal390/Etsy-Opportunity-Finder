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
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS radar_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            month_tag TEXT,
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


def save_radar_entries(entries: list):
    """Bulk-insert a list of scored query dicts (from radar.score_batch)."""
    if not entries:
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executemany(
        "INSERT INTO radar_entries (query, month_tag, data) VALUES (?, ?, ?)",
        [(e["query"], e["month_tag"], json.dumps(e)) for e in entries],
    )
    conn.commit()
    conn.close()


def load_radar_entries(month_tag: str = None) -> list:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if month_tag:
        c.execute(
            "SELECT data FROM radar_entries WHERE month_tag = ? ORDER BY id DESC",
            (month_tag,),
        )
    else:
        c.execute("SELECT data FROM radar_entries ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]


def list_radar_months() -> list:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT DISTINCT month_tag FROM radar_entries ORDER BY month_tag DESC")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]
