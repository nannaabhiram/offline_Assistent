import os
import mysql.connector
from dotenv import load_dotenv

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def load_env():
    # Load env from project config/.env
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dotenv_path = os.path.join(project_root, 'config', '.env')
    load_dotenv(dotenv_path=dotenv_path)


def get_conn():
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    dbname = os.getenv('MYSQL_DB')

    # Connect first to server (may fail if DB does not exist)
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password)
    except Exception as e:
        raise SystemExit(f"Failed to connect to MySQL server: {e}")

    cur = conn.cursor()
    # Ensure database exists
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}`")
    cur.execute(f"USE `{dbname}`")
    return conn


def run_schema(conn):
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    cursor = conn.cursor()

    # Execute statement by statement (simple splitter)
    for statement in [s.strip() for s in sql.split(';') if s.strip()]:
        try:
            cursor.execute(statement)
        except mysql.connector.Error as e:
            print(f"Error executing statement:\n{statement}\n-> {e}")
            raise
    conn.commit()


if __name__ == '__main__':
    load_env()
    conn = get_conn()
    run_schema(conn)
    print('Database schema applied successfully.')
