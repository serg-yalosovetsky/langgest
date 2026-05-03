from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any


class SQLiteStore:
    """Thread-safe SQLite store for macros, history, and key-value config."""

    def __init__(self, db_path: str | Path = "data/assistant.db") -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(str(self._path), check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_schema(self) -> None:
        conn = self._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS macros (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        conn.commit()

    def insert_event(self, event_type: str, data: dict[str, Any], timestamp: float) -> None:
        conn = self._conn()
        conn.execute(
            "INSERT INTO events (timestamp, type, data) VALUES (?, ?, ?)",
            (timestamp, event_type, json.dumps(data, ensure_ascii=False)),
        )
        conn.commit()

    def get_recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for row in rows:
            entry = dict(row)
            entry["data"] = json.loads(entry["data"])
            result.append(entry)
        return result

    def save_macro(self, macro_id: str, name: str, data: dict[str, Any], created_at: float) -> None:
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO macros (id, name, data, created_at) VALUES (?, ?, ?, ?)",
            (macro_id, name, json.dumps(data, ensure_ascii=False), created_at),
        )
        conn.commit()

    def get_macro(self, macro_id: str) -> dict[str, Any] | None:
        conn = self._conn()
        row = conn.execute("SELECT * FROM macros WHERE id = ?", (macro_id,)).fetchone()
        if row is None:
            return None
        entry = dict(row)
        entry["data"] = json.loads(entry["data"])
        return entry

    def set_kv(self, key: str, value: str) -> None:
        conn = self._conn()
        conn.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value))
        conn.commit()

    def get_kv(self, key: str, default: str | None = None) -> str | None:
        conn = self._conn()
        row = conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
