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

# for user interaction


def insert_task(conn, title, description, priority):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks(title,description,priority) VALUES (%s, %s, %s)",
        (title, description, priority)
    )
    conn.commit()
    cursor.close()


def fetch_tasks(conn, filter_by=None, filter_value=None):
    cursor = conn.cursor()
    if filter_by and filter_value:
        query = f"SELECT id, title, description, status, priority, created_at FROM tasks WHERE {filter_by} = %s"
        cursor.execute(query, (filter_value,))
    else:
        cursor.execute(
            "SELECT id, title, description, status, priority, created_at FROM tasks"
        )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def view_tasks(conn):
    print("\n=== View Tasks ===")
    print("1. Show all")
    print("2. Filter by status")
    print("3. Filter by priority")
    choice = input("Choose filter option: ").strip()

    filter_by = None
    filter_value = None

    if choice == "2":
        filter_value = input(
            "Enter status (todo/in_progress/done): ").strip().lower()
        if filter_value not in ['todo', 'in_progress', 'done']:
            print("Invalid status.")
            return
        filter_by = "status"
    elif choice == "3":
        filter_value = input(
            "Enter priority (low/medium/high): ").strip().lower()
        if filter_value not in ['low', 'medium', 'high']:
            print("Invalid priority.")
            return
        filter_by = "priority"

    rows = fetch_tasks(conn, filter_by, filter_value)

    if not rows:
        print("No tasks found.")
        return

    print(
        f"\n{'ID':<5} {'Title':<20} {'Status':<15} {'Priority':<10} {'Created At':<25}")
    print("-" * 75)
    for row in rows:
        print(
            f"{row[0]:<5} {row[1]:<20} {row[3]:<15} {row[4]:<10} {str(row[5]):<25}")


''' OLD code 
def fetch_tasks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    return rows


def view_tasks(conn):
    rows = fetch_tasks(conn)
    if not rows:
        print("No tasks found.")
        return

    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1]}, Description: {row[2]}, Status: {row[3]}, Priority: {row[4]}, Created At: {row[5]}, Completed At: {row[6]}")
'''

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
   # add_task(conn)
    view_tasks(conn)
