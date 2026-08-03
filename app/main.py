import os
import time
import psycopg2
from dotenv import load_dotenv

# need further clarification for this line befire it was
# load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

load_dotenv()


def connect_db():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST"),
                port=os.environ.get("DB_PORT"),
                dbname=os.environ.get("DB_NAME"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD")
            )
            print("Database connection successful")
            return conn
        except psycopg2.OperationalError as e:
            retries -= 1
            print(e)
            print(
                f"Database not ready, retry in 2 seconds....({retries} retries left) ")
            time.sleep(2)

    print("Failed to connect to database after multiple retries")
    exit(1)


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    print("Tasks table ready")


if __name__ == "__main__":
    conn = connect_db()
    create_table(conn)
