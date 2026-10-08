import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "debuggenie.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# ============================================================
# CREATE TABLES
# ============================================================

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)

    # Analysis history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_email TEXT,
            file_name TEXT,
            language TEXT,
            code TEXT,
            success INTEGER,
            error_type TEXT,
            error_message TEXT,
            error_line TEXT,
            suggestion TEXT,
            analyzed_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(name, email, password):
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        email = email.strip().lower()

        # Check whether email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()

            return {
                "success": False,
                "message": "An account with this email already exists."
            }

        password_hash = hash_password(password)

        cursor.execute("""
            INSERT INTO users
            (name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name.strip(),
            email,
            password_hash,
            "user",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return {
            "success": True,
            "id": user_id,
            "name": name.strip(),
            "email": email,
            "role": "user",
            "message": "Registration successful."
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "An account with this email already exists."
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Registration failed: {error}"
        }


# ============================================================
# LOGIN USER
# ============================================================

def login_user(email, password):
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        email = email.strip().lower()
        password_hash = hash_password(password)

        cursor.execute("""
            SELECT id, name, email, password_hash, role
            FROM users
            WHERE email = ?
        """, (email,))

        user = cursor.fetchone()

        conn.close()

        if user is None:
            return {
                "success": False,
                "message": "No account found with this email."
            }

        user_id, name, db_email, db_password, role = user

        if password_hash != db_password:
            return {
                "success": False,
                "message": "Incorrect password."
            }

        return {
            "success": True,
            "id": user_id,
            "name": name,
            "email": db_email,
            "role": role,
            "message": "Login successful."
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Login failed: {error}"
        }


# ============================================================
# GET USER BY ID
# ============================================================

def get_user_by_id(user_id):
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, role, created_at
            FROM users
            WHERE id = ?
        """, (user_id,))

        user = cursor.fetchone()

        conn.close()

        if not user:
            return None

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "created_at": user[4]
        }

    except Exception:
        return None


# ============================================================
# GET ALL USERS
# ============================================================

def get_all_users():
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, role, created_at
            FROM users
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        conn.close()

        users = []

        for row in rows:
            users.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "role": row[3],
                "created_at": row[4]
            })

        return users

    except Exception:
        return []


# ============================================================
# SAVE ANALYSIS HISTORY
# ============================================================

def save_analysis_history(
    user_id,
    user_email,
    file_name,
    language,
    code,
    success,
    error_type,
    error_message,
    error_line,
    suggestion
):
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO analysis_history (
                user_id,
                user_email,
                file_name,
                language,
                code,
                success,
                error_type,
                error_message,
                error_line,
                suggestion,
                analyzed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_email,
            file_name,
            language,
            code,
            1 if success else 0,
            error_type,
            error_message,
            str(error_line),
            suggestion,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return True

    except Exception as error:
        print("History save error:", error)
        return False


# ============================================================
# GET USER HISTORY
# ============================================================

def get_user_history(user_id):
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                user_id,
                user_email,
                file_name,
                language,
                code,
                success,
                error_type,
                error_message,
                error_line,
                suggestion,
                analyzed_at
            FROM analysis_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))

        rows = cursor.fetchall()

        conn.close()

        history = []

        for row in rows:
            history.append({
                "id": row[0],
                "user_id": row[1],
                "user_email": row[2],
                "file_name": row[3],
                "language": row[4],
                "code": row[5],
                "success": bool(row[6]),
                "error_type": row[7],
                "error_message": row[8],
                "error_line": row[9],
                "suggestion": row[10],
                "analyzed_at": row[11]
            })

        return history

    except Exception as error:
        print("History error:", error)
        return []


# ============================================================
# GET ALL HISTORY - ADMIN
# ============================================================

def get_all_history():
    try:
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                user_id,
                user_email,
                file_name,
                language,
                code,
                success,
                error_type,
                error_message,
                error_line,
                suggestion,
                analyzed_at
            FROM analysis_history
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        conn.close()

        history = []

        for row in rows:
            history.append({
                "id": row[0],
                "user_id": row[1],
                "user_email": row[2],
                "file_name": row[3],
                "language": row[4],
                "code": row[5],
                "success": bool(row[6]),
                "error_type": row[7],
                "error_message": row[8],
                "error_line": row[9],
                "suggestion": row[10],
                "analyzed_at": row[11]
            })

        return history

    except Exception as error:
        print("All history error:", error)
        return []


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_database()