import mysql.connector
from dotenv import load_dotenv
import os
import datetime
from typing import Tuple
import bcrypt

# Load env from project root regardless of current working directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOTENV_PATH = os.path.join(PROJECT_ROOT, 'config', '.env')
load_dotenv(dotenv_path=DOTENV_PATH)

user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST") or "127.0.0.1"
port = int(os.getenv("MYSQL_PORT") or 3306)
db = os.getenv("MYSQL_DB")

# Normalize host: avoid named pipe/shared memory by forcing TCP
if host in (".", "localhost"):
    host = "127.0.0.1"

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db
        )
    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# 🔹 USERS
def get_or_create_user(name):
    """Legacy helper used by switch flows. If user doesn't exist, create without password.

    NOTE: Preferred flows should use create_user_with_password. This remains for backward
    compatibility but may be restricted in the future.
    """
    db_conn = get_db_connection()
    if not db_conn:
        print("⚠️ Skipping get_or_create_user: DB not available.")
        return None
    cursor = db_conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
    user = cursor.fetchone()

    if user:
        return user["id"]

    cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
    db_conn.commit()
    return cursor.lastrowid


def get_all_users():
    """Return a list of all users as dictionaries: [{id, name, created_at}]"""
    db_conn = get_db_connection()
    if not db_conn:
        return []
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, created_at FROM users ORDER BY created_at DESC")
    return cursor.fetchall()


# 🔹 TASKS
def save_task(db, title, user_id=None, due_date=None, status="pending"):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, status, due_date, user_id) VALUES (%s, %s, %s, %s)",
        (title, status, due_date, user_id),
    )
    db.commit()


def get_tasks_for_user_on_date(user_id, date_str):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, title, status, due_date
        FROM tasks
        WHERE user_id = %s AND DATE(created_at) = %s
        """,
        (user_id, date_str),
    )
    return cursor.fetchall()


# 🔹 CONVERSATIONS
def save_conversation(db, user_input, assistant_response):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO conversations (user_input, assistant_response, timestamp) VALUES (%s, %s, %s)",
        (user_input, assistant_response, datetime.datetime.now()),
    )
    db.commit()


# 🔹 DELETED TASKS (for history)
def get_deleted_tasks():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM deleted_tasks ORDER BY deleted_at DESC LIMIT 10")
    return cursor.fetchall()


# 🔹 LOGS
def log_action(action, status="success"):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO system_logs (action, status, timestamp) VALUES (%s, %s, %s)",
        (action, status, datetime.datetime.now()),
    )
    db.commit()


def get_system_logs(limit=10):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
    return cursor.fetchall()


# 🔹 SECURITY: Verify DB password before destructive actions
def verify_db_password(candidate_password: str) -> bool:
    """Return True if the provided password can authenticate to the configured MySQL server.

    We attempt a short-lived connection using the same host/port/user but the provided password.
    This is safer than comparing to env text and also supports rotated secrets.
    """
    try:
        mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=candidate_password,
            database=db,
        ).close()
        return True
    except Exception:
        return False


def delete_user_by_name(name: str) -> Tuple[bool, str]:
    """Delete a user and their related records safely.

    Since the schema does not specify ON DELETE CASCADE for tasks, this function
    will first delete tasks that reference the user, then delete the user.

    Returns (success, message).
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection not available."

    cur = conn.cursor()
    try:
        # Look up the user id
        cur.execute("SELECT id FROM users WHERE name = %s", (name,))
        row = cur.fetchone()
        if not row:
            return False, f"User '{name}' not found."
        user_id = row[0]

        # Delete dependent tasks first (no cascade in schema)
        cur.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))

        # Finally delete the user
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return True, f"User '{name}' and related tasks deleted."
    except Exception as e:
        conn.rollback()
        return False, f"Error deleting user: {e}"
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def user_has_password(name: str) -> bool:
    """Return True if the user exists and has a non-null password_hash."""
    _ensure_users_password_column()
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM users WHERE name = %s", (name,))
        row = cur.fetchone()
        return bool(row and row[0])
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def set_user_password(name: str, plain_password: str) -> Tuple[bool, str]:
    """Set or update a user's password. Returns (ok, message)."""
    _ensure_users_password_column()
    conn = get_db_connection()
    if not conn:
        return False, "Database connection not available."
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE name = %s", (name,))
        row = cur.fetchone()
        if not row:
            return False, f"User '{name}' not found."
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")
        cur.execute("UPDATE users SET password_hash = %s WHERE name = %s", (pwd_hash, name))
        conn.commit()
        return True, "Password updated."
    except Exception as e:
        conn.rollback()
        return False, f"Error setting password: {e}"
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


# --- User password management ---
def _ensure_users_password_column():
    """Ensure users table has a password_hash column."""
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'password_hash'
            """,
            (db,),
        )
        exists = cur.fetchone()[0] > 0
        if not exists:
            cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL")
            conn.commit()
    except Exception:
        # Do not raise; best-effort
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def user_exists(name: str) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM users WHERE name = %s", (name,))
        return cur.fetchone() is not None
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def create_user_with_password(name: str, plain_password: str) -> Tuple[bool, str, int]:
    """Create user with bcrypt-hashed password. Returns (ok, message, user_id)."""
    _ensure_users_password_column()
    conn = get_db_connection()
    if not conn:
        return False, "Database connection not available.", -1
    cur = conn.cursor()
    try:
        # Check name uniqueness
        cur.execute("SELECT id FROM users WHERE name = %s", (name,))
        if cur.fetchone():
            return False, f"User '{name}' already exists.", -1
        # Hash password
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")
        cur.execute("INSERT INTO users (name, password_hash) VALUES (%s, %s)", (name, pwd_hash))
        conn.commit()
        return True, "User created.", cur.lastrowid
    except Exception as e:
        conn.rollback()
        return False, f"Error creating user: {e}", -1
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def verify_user_password(name: str, plain_password: str) -> bool:
    _ensure_users_password_column()
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM users WHERE name = %s", (name,))
        row = cur.fetchone()
        if not row or not row[0]:
            return False
        stored = row[0].encode("utf-8")
        return bcrypt.checkpw(plain_password.encode("utf-8"), stored)
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
