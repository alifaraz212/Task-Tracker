import pytest
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

from app.main import (
    create_table,
    insert_task,
    fetch_tasks,
    fetch_task_by_id,
    update_task_db,
    delete_task_db,
)

load_dotenv()

# ===========================================================================
# FIXTURE — Prepares a real DB connection for every test.
# yield = setup above, cleanup below. Replaces setUp/tearDown.
# ===========================================================================

@pytest.fixture(scope="function")
def db_conn():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
    create_table(conn)
    yield conn
    conn.close()


# ===========================================================================
# FIXTURE — Tracks inserted IDs so we clean up only our own rows after tests.
# Hotel room rule: leave it exactly as you found it.
# ===========================================================================

@pytest.fixture(scope="function")
def inserted_ids(db_conn):
    ids = []
    yield ids
    if ids:
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ANY(%s)", (ids,))
        db_conn.commit()
        cursor.close()


# ===========================================================================
# HELPER — Inserts a row and returns its ID immediately via RETURNING id.
# We need the ID for cleanup. PostgreSQL assigns it — we can't know it in advance.
# ===========================================================================

def insert_and_get_id(conn, title="Test Task", description="Desc", priority="medium"):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks(title, description, priority) VALUES (%s, %s, %s) RETURNING id",
        (title, description, priority),
    )
    task_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    return task_id


# ===========================================================================
# TESTS — pytest finds any function/method starting with test_
# No class inheritance needed unlike unittest.
# ===========================================================================

class TestInsertTask:

    def test_insert_creates_row(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Buy groceries", "Milk and eggs", "low")
        inserted_ids.append(task_id)

        task = fetch_task_by_id(db_conn, task_id)
        assert task is not None
        assert task["title"] == "Buy groceries"
        assert task["status"] == "todo"       # clear: we're checking status
        assert task["priority"] == "low"      # clear: we're checking priority

    def test_insert_default_status_is_todo(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Default status check")
        inserted_ids.append(task_id)

        task = fetch_task_by_id(db_conn, task_id)
        assert task["status"] == "todo"

    def test_insert_with_high_priority(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Urgent task", "Do it now", "high")
        inserted_ids.append(task_id)

        task = fetch_task_by_id(db_conn, task_id)
        assert task["priority"] == "high"


class TestFetchTasks:

    def test_fetch_all_returns_list(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Fetch test task")
        inserted_ids.append(task_id)

        rows = fetch_tasks(db_conn)
        assert isinstance(rows, list)
        assert len(rows) >= 1

    def test_fetch_filter_by_priority(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "High prio task", priority="high")
        inserted_ids.append(task_id)

        rows = fetch_tasks(db_conn, filter_by="priority", filter_value="high")
        for row in rows:
            assert row["priority"] == "high"

    def test_fetch_filter_by_status(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Status filter task")
        inserted_ids.append(task_id)

        rows = fetch_tasks(db_conn, filter_by="status", filter_value="todo")
        for row in rows:
            assert row["status"] == "todo"


class TestUpdateTask:

    def test_update_title(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Old Title")
        inserted_ids.append(task_id)

        result = update_task_db(db_conn, task_id, "title", "New Title")
        assert result is True

        task = fetch_task_by_id(db_conn, task_id)
        assert task["title"] == "New Title"

    def test_update_status_to_done_sets_completed_at(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Task to complete")
        inserted_ids.append(task_id)

        update_task_db(db_conn, task_id, "status", "done")

        cursor = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT completed_at FROM tasks WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        cursor.close()

        assert row["completed_at"] is not None

    def test_update_nonexistent_task_returns_false(self, db_conn):
        result = update_task_db(db_conn, 999999, "title", "Ghost")
        assert result is False

    def test_update_invalid_field_returns_false(self, db_conn):
        result = update_task_db(db_conn, 1, "hacked_field", "value")
        assert result is False


class TestDeleteTask:

    def test_delete_existing_task(self, db_conn):
        task_id = insert_and_get_id(db_conn, "Task to delete")

        result = delete_task_db(db_conn, task_id)
        assert result is True

        task = fetch_task_by_id(db_conn, task_id)
        assert task is None

    def test_delete_nonexistent_task_returns_false(self, db_conn):
        result = delete_task_db(db_conn, 999999)
        assert result is False


class TestFetchTaskById:

    def test_fetch_existing_task(self, db_conn, inserted_ids):
        task_id = insert_and_get_id(db_conn, "Lookup task", "Some desc", "medium")
        inserted_ids.append(task_id)

        task = fetch_task_by_id(db_conn, task_id)
        assert task is not None
        assert task["id"] == task_id

    def test_fetch_nonexistent_task_returns_none(self, db_conn):
        task = fetch_task_by_id(db_conn, 999999)
        assert task is None
