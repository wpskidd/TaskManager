"""Task model and management logic.

This module knows nothing about the command line; it works with a
:class:`~taskmanager.storage.JsonStorage` instance for persistence and
raises :class:`TaskError` subclasses for invalid operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .storage import JsonStorage


class TaskError(Exception):
    """Base class for all task-management errors."""


class TaskNotFoundError(TaskError):
    """Raised when an operation references a task ID that does not exist."""


class InvalidTaskError(TaskError):
    """Raised when a task cannot be created because its input is invalid."""


@dataclass
class Task:
    """A single task.

    Attributes:
        id: Unique, positive integer identifier.
        description: Human-readable task description.
        created_at: Creation timestamp as an ISO 8601 string (UTC).
        completed: Whether the task has been completed.
    """

    id: int
    description: str
    created_at: str
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "created_at": self.created_at,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=int(data["id"]),
            description=str(data["description"]),
            created_at=str(data.get("created_at", "")),
            completed=bool(data.get("completed", False)),
        )


class TaskManager:
    """Manages a collection of tasks backed by a :class:`JsonStorage`.

    The manager loads all tasks on construction and re-saves them after
    every mutating operation, so state always survives between runs.
    """

    def __init__(self, storage: JsonStorage) -> None:
        self._storage = storage
        self._tasks: list[Task] = []
        self.load()

    # -- persistence -------------------------------------------------------

    def load(self) -> list[Task]:
        """Reload tasks from storage, replacing the in-memory list."""
        self._tasks = [Task.from_dict(item) for item in self._storage.load()]
        return self._tasks

    def save(self) -> None:
        """Persist the current in-memory tasks to storage."""
        self._storage.save(self._tasks)

    # -- queries -----------------------------------------------------------

    def list(self) -> list[Task]:
        """Return all tasks, in creation order."""
        return list(self._tasks)

    def get(self, task_id: int) -> Task:
        """Return the task with the given ID.

        Raises:
            TaskNotFoundError: if no task has that ID.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"No task with ID {task_id}.")

    # -- mutations ---------------------------------------------------------

    def add(self, description: str) -> Task:
        """Create a new task with a unique ID and persist it.

        Raises:
            InvalidTaskError: if the description is empty or whitespace-only.
        """
        cleaned = (description or "").strip()
        if not cleaned:
            raise InvalidTaskError("Task description must not be empty.")
        task = Task(
            id=self._next_id(),
            description=cleaned,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._tasks.append(task)
        self.save()
        return task

    def complete(self, task_id: int) -> Task:
        """Mark the task with the given ID as completed and persist it.

        Raises:
            TaskNotFoundError: if no task has that ID.
        """
        task = self.get(task_id)
        task.completed = True
        self.save()
        return task

    def delete(self, task_id: int) -> Task:
        """Remove the task with the given ID and persist the change.

        Raises:
            TaskNotFoundError: if no task has that ID.
        """
        task = self.get(task_id)
        self._tasks.remove(task)
        self.save()
        return task

    # -- helpers -----------------------------------------------------------

    def _next_id(self) -> int:
        """Return the next unique ID (max existing ID + 1, or 1)."""
        return max((task.id for task in self._tasks), default=0) + 1
