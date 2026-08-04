# Task-Tracker
# Task Tracker

A simple command-line Task Tracker application built with **Python** and **PostgreSQL**, containerized using **Docker** and **Docker Compose**. The application allows users to manage tasks, track their status, and view task statistics.

---

## Features

* Add new tasks
* View all tasks with optional filtering by status or priority
* Update existing tasks
* Delete tasks with confirmation
* View task statistics, including average completion time

---

## Technologies Used

* Python 3.11
* PostgreSQL 15
* Docker
* Docker Compose
* psycopg2 (database driver)
* python-dotenv (environment variable management)

---

## Project Structure

```text
task-tracker/
├── docker-compose.yml
├── README.md
├── .gitignore
└── app/
    ├── Dockerfile
    ├── .dockerignore
    ├── requirements.txt
    └── main.py
```

---

## Getting Started

### Prerequisites

* Docker Desktop installed and running

No additional software is required.

### Clone the Repository

```bash
git clone https://github.com/alifaraz212/Task-Tracker.git
cd Task-Tracker
```

### Run the Application

Build and start both containers:

```bash
docker compose up --build
```

---

## Interact with the Application

After starting the containers, open a new terminal and attach to the application container:

```bash
docker attach task-tracker-app-1
```

If the menu does not appear immediately, press **Enter**.

You will see:

```text
=== Task Tracker Menu ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. View Status
6. Exit
```

Enter the desired option number and press **Enter**.

---

## Stop the Application

```bash
docker compose down
```

---

## Task Fields

| Field            | Description                                       |
| ---------------- | ------------------------------------------------- |
| **id**           | Auto-generated unique identifier                  |
| **title**        | Required task title                               |
| **description**  | Optional task description                         |
| **status**       | `todo`, `in_progress`, or `done`                  |
| **priority**     | `low`, `medium`, or `high`                        |
| **created_at**   | Automatically set when a task is created          |
| **completed_at** | Automatically set when a task is marked as `done` |

---

## Design Decisions

* **Raw SQL over ORM:** Used `psycopg2` with parameterized SQL queries instead of an ORM to strengthen SQL skills while preventing SQL injection.
* **Single Responsibility Principle:** Functions are separated by responsibility. User interaction, database operations, and application logic are kept independent.
* **Retry Logic:** The application retries the database connection up to **5 times** with a **2-second delay** to handle PostgreSQL startup timing inside Docker.
* **Environment Variables:** Database credentials are loaded from environment variables using `python-dotenv` instead of being hardcoded.
* **Named Docker Volume:** PostgreSQL data is stored in a named Docker volume so tasks persist even if containers are restarted.
* **Delete Confirmation:** Before deleting a task, the application displays its details and asks for confirmation to prevent accidental deletion.

---

## Author

**Ali Faraz**
