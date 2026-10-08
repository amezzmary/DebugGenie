import sqlite3
import hashlib
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "debuggenie.db"


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def create_users_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def register_user(name, email, password):

    create_users_table()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:

        password_hash = hash_password(password)

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
                "user"
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def login_user(email, password):

    create_users_table()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute(
        """
        SELECT id, name, email, role
        FROM users
        WHERE email = ?
        AND password_hash = ?
        """,
        (
            email,
            password_hash
        )
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3]
        }

    return None