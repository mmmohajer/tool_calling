import json
import re
from datetime import date
from pathlib import Path

_TASKS_PATH = Path(__file__).parent.parent / "tasks.json"
_STATUSES = {"todo", "in_progress", "done"}


def load_tasks() -> list[dict]:
    if not _TASKS_PATH.exists():
        return []
    text = _TASKS_PATH.read_text().strip()
    if not text:
        return []
    tasks = json.loads(text)
    if not isinstance(tasks, list):
        raise ValueError("tasks.json must be an array")
    return tasks


def save_tasks(tasks: list[dict]) -> None:
    _TASKS_PATH.write_text(json.dumps(tasks, indent=2) + "\n")


def find_task(tasks: list[dict], task_id: int) -> dict:
    for task in tasks:
        if task.get("id") == task_id:
            return task
    raise ValueError(f"task {task_id} was not found")


def require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or value.strip() == "" or value != value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def require_status(value: str) -> str:
    if value not in _STATUSES:
        allowed = ", ".join(sorted(_STATUSES))
        raise ValueError(f"status must be one of: {allowed}")
    return value


def require_due_date(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("due_date must be a YYYY-MM-DD string")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError("due_date must be a YYYY-MM-DD string") from None
    return value


def require_pattern(value: str) -> re.Pattern[str]:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError("pattern must be a non-empty regular expression")
    try:
        return re.compile(value)
    except re.error as exc:
        raise ValueError(f"pattern is not a valid regular expression ({exc})") from exc


def require_task_id(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value
