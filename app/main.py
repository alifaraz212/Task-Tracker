import os
import time
import psycopg2
from dotenv import load_dotenv


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

# for db interaction


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

# ========================= Update Task ========================


def update_task_db(conn, task_id, field, new_value):
    allowed_fields = ["title", "description", "status", "priority"]
    if field not in allowed_fields:
        return False

    cursor = conn.cursor()

    if field == "status" and new_value == "done":
        # when marked done, automatically set completed_at timestamp
        cursor.execute(
            "UPDATE tasks SET status = %s, completed_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_value, task_id)
        )
    else:
        query = f"UPDATE tasks SET {field} = %s WHERE id = %s"
        cursor.execute(query, (new_value, task_id))

    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    return success


def update_task(conn):
    print("\n=== Update Task ===")
    try:
        task_id = int(input("Enter task ID: ").strip())
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    field = input(
        "Which field to update? (title/description/status/priority): ").strip().lower()
    if field not in ['title', 'description', 'status', 'priority']:
        print("Invalid field.")
        return

    if field == "status":
        new_value = input(
            "Enter new status (todo/in_progress/done): ").strip().lower()
        if new_value not in ['todo', 'in_progress', 'done']:
            print("Invalid status.")
            return
    elif field == "priority":
        new_value = input(
            "Enter new priority (low/medium/high): ").strip().lower()
        if new_value not in ['low', 'medium', 'high']:
            print("Invalid priority.")
            return
    else:
        new_value = input("Enter new value: ").strip()
        if not new_value:
            print("Value cannot be empty.")
            return

    success = update_task_db(conn, task_id, field, new_value)
    if success:
        print("Task updated successfully!")
    else:
        print("Task not found.")

# ========================= Delete Task ========================


def delete_task_db(conn, task_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    return success


def fetch_task_by_id(conn, task_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, status, priority FROM tasks WHERE id = %s",
        (task_id,)
    )
    task = cursor.fetchone()
    cursor.close()
    return task


def delete_task(conn):
    print("\n=== Delete Task ===")
    try:
        task_id = int(input("Enter task ID to delete: ").strip())
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    task = fetch_task_by_id(conn, task_id)

    if not task:
        print("Task not found.")
        return

    print(
        f"\nTask found: ID={task[0]}, Title={task[1]}, Status={task[2]}, Priority={task[3]}")
    confirm = input(
        "Are you sure you want to delete this task? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Delete cancelled.")
        return

    success = delete_task_db(conn, task_id)
    if success:
        print("Task deleted successfully.")
    else:
        print("Something went wrong.")

# ========================= View Status ========================


def view_status(conn):
    print("\n=== Task Status ===")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    print(f"Total tasks: {total}")

    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    statuses = cursor.fetchall()
    print("\nTasks by status:")
    for row in statuses:
        print(f"  {row[0]}: {row[1]}")

    cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
    priorities = cursor.fetchall()
    print("\nTasks by priority:")
    for row in priorities:
        print(f"  {row[0]}: {row[1]}")

    cursor.execute("""
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 3600)
        FROM tasks
        WHERE completed_at IS NOT NULL
    """)
    avg = cursor.fetchone()[0]
    if avg:
        print(f"\nAverage completion time: {avg:.2f} hours")
    else:
        print("\nNo completed tasks yet.")

    cursor.close()


def show_menu():
    print("\n=== Task Tracker Menu ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. View Status")
    print("6. Exit")


if __name__ == "__main__":
    conn = connect_db()
    create_table(conn)
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(conn)
        elif choice == "2":
            view_tasks(conn)
        elif choice == "3":
            update_task(conn)
        elif choice == "4":
            delete_task(conn)
        elif choice == "5":
            view_status(conn)
        elif choice == "6":
            print("Closing connection. Goodbye!")
            conn.close()
            break
        else:
            print("Invalid option. Please choose between 1 and 6.")
