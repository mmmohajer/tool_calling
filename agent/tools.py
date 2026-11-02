from datetime import date

from agent.helpers import (
    find_task,
    load_tasks,
    require_due_date,
    require_pattern,
    require_status,
    require_task_id,
    require_text,
    save_tasks,
)


def get_todays_date() -> str:
    """Return today's date as YYYY-MM-DD."""
    return date.today().isoformat()


def create_task(title: str, description: str, status: str, due_date: str) -> dict:
    """Add a task. Its id is one greater than the id of the last task."""
    tasks = load_tasks()
    task = {
        "id": 1 if not tasks else require_task_id(tasks[-1]["id"], "last task") + 1,
        "title": require_text(title, "title"),
        "description": require_text(description, "description"),
        "status": require_status(status),
        "due_date": require_due_date(due_date),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def filter_tasks_by_text(pattern: str) -> list[dict]:
    """Return tasks whose title or description matches this regular expression."""
    compiled = require_pattern(pattern)
    return [
        task
        for task in load_tasks()
        if compiled.search(str(task.get("title", "")))
        or compiled.search(str(task.get("description", "")))
    ]


def filter_tasks_by_due_date(due_date: str) -> list[dict]:
    """Return tasks whose due date is exactly this date."""
    expected = require_due_date(due_date)
    return [task for task in load_tasks() if task.get("due_date") == expected]


def filter_tasks_by_status(status: str) -> list[dict]:
    """Return tasks with this status."""
    expected = require_status(status)
    return [task for task in load_tasks() if task.get("status") == expected]


def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    due_date: str | None = None,
) -> dict:
    """Change the given fields of the task with this id."""
    changes = {}
    if title is not None:
        changes["title"] = require_text(title, "title")
    if description is not None:
        changes["description"] = require_text(description, "description")
    if status is not None:
        changes["status"] = require_status(status)
    if due_date is not None:
        changes["due_date"] = require_due_date(due_date)
    if not changes:
        raise ValueError("update needs at least one field to change")

    tasks = load_tasks()
    task = find_task(tasks, require_task_id(task_id, "task_id"))
    task.update(changes)
    save_tasks(tasks)
    return task


def delete_task(task_id: int) -> dict:
    """Remove the task with this id and return it."""
    tasks = load_tasks()
    expected = require_task_id(task_id, "task_id")
    for index, task in enumerate(tasks):
        if task.get("id") == expected:
            deleted = tasks.pop(index)
            save_tasks(tasks)
            return deleted
    raise ValueError(f"task {expected} was not found")


by_name = {
    "get_todays_date": get_todays_date,
    "create_task": create_task,
    "filter_tasks_by_text": filter_tasks_by_text,
    "filter_tasks_by_due_date": filter_tasks_by_due_date,
    "filter_tasks_by_status": filter_tasks_by_status,
    "update_task": update_task,
    "delete_task": delete_task,
}

definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_todays_date",
            "description": "Return today's date as YYYY-MM-DD.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Add a task. The id is assigned automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
                    "due_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["title", "description", "status", "due_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_tasks_by_text",
            "description": (
                "Find tasks whose title or description matches a regular expression. "
                "Each task includes its id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regular expression."},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_tasks_by_due_date",
            "description": "Return tasks due on this exact date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "due_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["due_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_tasks_by_status",
            "description": "Return tasks with this status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
                },
                "required": ["status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Change a task by id. Find the id with filter_tasks_by_text when the user did not give one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
                    "due_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by id. Find the id with filter_tasks_by_text when the user did not give one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
]
