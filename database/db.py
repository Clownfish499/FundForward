import os
import sqlite3
from config import Config


def get_db_connection(db_path=None):
    """Return a SQLite connection with Row factory and foreign keys enabled."""
    path = db_path or Config.DATABASE_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema(db_path=None):
    """Execute schema.sql to initialize all tables."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn = get_db_connection(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()
