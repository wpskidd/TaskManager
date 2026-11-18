"""A simple command-line task manager.

Modules:
    cli      -- command-line interface (argparse)
    tasks    -- task model and management logic
    storage  -- JSON file persistence
"""

from .storage import JsonStorage, StorageError
from .tasks import (
    InvalidTaskError,
    Task,
    TaskError,
    TaskManager,
    TaskNotFoundError,
)

__all__ = [
    "InvalidTaskError",
    "JsonStorage",
    "StorageError",
    "Task",
    "TaskError",
    "TaskManager",
    "TaskNotFoundError",
]
