import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os
import datetime
import threading
import time

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

# Connection pool for better performance
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    """Get or create a connection pool for better performance"""
    global _connection_pool
    with _pool_lock:
        if _connection_pool is None:
            try:
                _connection_pool = pooling.MySQLConnectionPool(
                    pool_name="assistant_pool",
                    pool_size=5,  # Keep 5 connections in pool
                    pool_reset_session=False,
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=db,
                    autocommit=False  # We'll manage transactions manually
                )
            except Exception as e:
                print("❌ Connection pool creation error:", e)
                return None
        return _connection_pool

def get_db_connection():
    """Get a connection from the pool"""
    try:
        pool = get_connection_pool()
        if pool is None:
            return None
        return pool.get_connection()
    except Exception as e:
        print("❌ Database connection error:", e)
        return None


# 🔹 TASKS
def save_task(db, title, due_date=None, status="pending"):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (title, status, due_date) VALUES (%s, %s, %s)",
            (title, status, due_date),
        )
        db.commit()
    finally:
        cursor.close()


def get_tasks_on_date(date_str):
    db = get_db_connection()
    if not db:
        return []
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, status, due_date
            FROM tasks
            WHERE DATE(created_at) = %s
            """,
            (date_str,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


# 🔹 CONVERSATIONS
def save_conversation(db, user_input, assistant_response):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO conversations (user_input, assistant_response, timestamp) VALUES (%s, %s, %s)",
            (user_input, assistant_response, datetime.datetime.now()),
        )
        db.commit()
    finally:
        cursor.close()


# 🔹 DELETED TASKS (for history)
def get_deleted_tasks():
    db = get_db_connection()
    if not db:
        return []
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM deleted_tasks ORDER BY deleted_at DESC LIMIT 10")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


# 🔹 LOGS
def log_action(action, status="success"):
    db = get_db_connection()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO system_logs (action, status, timestamp) VALUES (%s, %s, %s)",
            (action, status, datetime.datetime.now()),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()


def get_system_logs(limit=10):
    db = get_db_connection()
    if not db:
        return []
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


# 🔹 MEMORIES (long-term small facts)
def ensure_memories_table():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content TEXT NOT NULL,
                tags VARCHAR(255) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        conn.commit()
    except Exception:
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


def save_memory(content: str, tags: str | None = None) -> int:
    conn = get_db_connection()
    if not conn:
        return -1
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO memories (content, tags) VALUES (%s, %s)",
            (content, tags),
        )
        conn.commit()
        return cur.lastrowid
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return -1
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def get_recent_memories(limit: int = 20):
    conn = get_db_connection()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, content, tags, created_at FROM memories ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return cur.fetchall()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def search_memories(query: str, limit: int = 10):
    conn = get_db_connection()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    try:
        q = f"%{query}%"
        cur.execute(
            "SELECT id, content, tags, created_at FROM memories WHERE (content LIKE %s OR tags LIKE %s) ORDER BY created_at DESC LIMIT %s",
            (q, q, limit),
        )
        return cur.fetchall()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def delete_memory_by_id(mem_id: int) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM memories WHERE id = %s", (mem_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
