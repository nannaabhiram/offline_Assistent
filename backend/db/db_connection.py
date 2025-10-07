import mysql.connector
from dotenv import load_dotenv
import os
import datetime

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


# 🔹 TASKS
def save_task(db, title, due_date=None, status="pending"):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, status, due_date) VALUES (%s, %s, %s)",
        (title, status, due_date),
    )
    db.commit()


def get_tasks_on_date(date_str):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, title, status, due_date
        FROM tasks
        WHERE DATE(created_at) = %s
        """,
        (date_str,),
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
