"""Small local persistence layer for the Receipt Streamlit app.

Product data remains in the checked-in CSV files. SQLite is used for the
small amount of mutable data: users and their saved shopping lists.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3

import bcrypt


DB_PATH = Path(__file__).resolve().parent / "receipt_local.db"


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialise():
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL REFERENCES users(email),
                store TEXT NOT NULL,
                input_items TEXT NOT NULL,
                matched_items TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def create_user(email: str, password: str):
    initialise()
    email = email.strip().lower()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        with _connect() as connection:
            connection.execute(
                "INSERT INTO users(email, password_hash, created_at) VALUES (?, ?, ?)",
                (email, password_hash, datetime.now(timezone.utc).isoformat()),
            )
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists."
    return True, "Account created."


def authenticate(email: str, password: str):
    initialise()
    with _connect() as connection:
        row = connection.execute(
            "SELECT email, password_hash FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    if not row or not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return None
    return {"email": row["email"]}


def save_list(email, store, input_items, matched_items):
    initialise()
    with _connect() as connection:
        connection.execute(
            "INSERT INTO shopping_lists(user_email, store, input_items, matched_items, created_at) VALUES (?, ?, ?, ?, ?)",
            (email.lower(), store, json.dumps(input_items), json.dumps(matched_items), datetime.now(timezone.utc).isoformat()),
        )


def get_lists(email):
    initialise()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id, user_email, store, input_items, matched_items, created_at FROM shopping_lists WHERE user_email = ? ORDER BY created_at DESC",
            (email.lower(),),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_list(list_id, email):
    initialise()
    with _connect() as connection:
        connection.execute("DELETE FROM shopping_lists WHERE id = ? AND user_email = ?", (list_id, email.lower()))
