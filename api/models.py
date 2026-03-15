import sqlite3
import os
from config import DB_PATH

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY,
            slug        TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            sort_order  INTEGER NOT NULL,
            num_nominees INTEGER DEFAULT 5
        );

        CREATE TABLE IF NOT EXISTS nominees (
            id          INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
            name        TEXT NOT NULL,
            subtitle    TEXT,
            is_winner   BOOLEAN DEFAULT FALSE,
            UNIQUE(category_id, name)
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY,
            username      TEXT UNIQUE COLLATE NOCASE NOT NULL,
            pin_hash      TEXT NOT NULL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at  TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS picks (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
            nominee_id  INTEGER NOT NULL REFERENCES nominees(id) ON DELETE CASCADE,
            picked_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, category_id)
        );

        CREATE INDEX IF NOT EXISTS idx_picks_user ON picks(user_id);
        CREATE INDEX IF NOT EXISTS idx_nominees_category ON nominees(category_id);
    """)
    db.commit()
    db.close()
