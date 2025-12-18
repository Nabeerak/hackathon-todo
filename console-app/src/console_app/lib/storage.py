"""Simple file-based storage for TodoManager state."""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from console_app.lib.todo_manager import TodoManager


def get_storage_path() -> Path:
    """Get the path to the storage file."""
    # Store in temp directory for Phase I
    storage_dir = Path.home() / ".console_todo"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir / "todos.json"


def save_state(manager: "TodoManager") -> None:
    """Save TodoManager state to disk.

    Args:
        manager: TodoManager instance to save
    """
    state = {
        "next_id": manager._next_id,
        "todos": {
            str(todo_id): {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "status": todo.status,
                "created_at": todo.created_at.isoformat(),
            }
            for todo_id, todo in manager._todos.items()
        },
    }

    storage_path = get_storage_path()
    with open(storage_path, "w") as f:
        json.dump(state, f, indent=2)


def load_state(manager: "TodoManager") -> None:
    """Load TodoManager state from disk.

    Args:
        manager: TodoManager instance to load into
    """
    from console_app.models.todo import Todo
    from datetime import datetime

    storage_path = get_storage_path()

    if not storage_path.exists():
        return  # No saved state yet

    try:
        with open(storage_path, "r") as f:
            state = json.load(f)

        manager._next_id = state["next_id"]
        manager._todos = {}

        for todo_id_str, todo_data in state["todos"].items():
            todo = Todo(
                id=todo_data["id"],
                title=todo_data["title"],
                description=todo_data["description"],
                status=todo_data["status"],
                created_at=datetime.fromisoformat(todo_data["created_at"]),
            )
            manager._todos[int(todo_id_str)] = todo
    except (json.JSONDecodeError, KeyError, ValueError):
        # Corrupted storage, start fresh
        pass


def clear_storage() -> None:
    """Clear the storage file (for testing)."""
    storage_path = get_storage_path()
    if storage_path.exists():
        os.remove(storage_path)
