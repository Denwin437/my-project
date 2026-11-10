"""SQLite storage layer. Uses parameterized queries only."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing

DB_PATH = os.environ.get("STUDENTS_DB", "students.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    course TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 8),
    gpa REAL NOT NULL CHECK (gpa BETWEEN 0 AND 4)
)
"""


def connect(path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str | None = None) -> None:
    with closing(connect(path)) as conn:
        conn.execute(SCHEMA)
        conn.commit()
