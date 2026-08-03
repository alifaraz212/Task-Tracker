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


def add_task(conn):
    print("\n===Add new Task===")
    title = input("Enter task title: ").strip()
    if not title:
        print("Task title cannot be empty.")
        return
    description = input("Enter task description: ").strip()
    priority = input(
        "Enter priority ('low', 'medium', 'high'): ").strip().lower()
    if priority not in ['low', 'medium', 'high']:
        print("Invalid priority. Defaulting to 'medium'.")
        priority = 'medium'
    insert_task(conn, title, description, priority)
    print("Task added successfully!")


def insert_task(conn, title, description, priority):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks(title,description,priority) VALUES (%s, %s, %s)",
        (title, description, priority)
    )
    conn.commit()
    cursor.close()


'''while True:
    print("\n===Task Tracker Menu===")
print("1. Add Task")
print("2. View Tasks")
print("3. Update Task")
print("4. Delete Task")
print("5. Status")
print("6. Exit")
choice = input("Choose an option: ")
'''

if __name__ == "__main__":
    conn = connect_db()
    create_table(conn)
    add_task(conn)
