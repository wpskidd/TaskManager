"""JSON file storage for tasks.

The storage layer is deliberately small: it knows how to read and write a
JSON file containing a list of task objects, and it raises :class:`StorageError`
for any problem it cannot handle gracefully (missing file is *not* an error,
an empty task list is returned instead).
"""

from __future__ import annotations

import json
import os
from typing import Any


class StorageError(Exception):
    """Raised when the JSON storage file cannot be read or written."""


class JsonStorage:
    """Persists tasks as a JSON array of objects in a single file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> list[dict[str, Any]]:
        """Return the stored tasks.

        A missing file is treated as an empty task list. A file that exists
        but contains invalid JSON (or JSON that is not a list of task
        objects) raises :class:`StorageError`.
        """
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise StorageError(
                f"Malformed JSON in {self.path!r}: {exc}"
            ) from exc
        except OSError as exc:
            raise StorageError(
                f"Cannot read {self.path!r}: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise StorageError(
                f"Expected a JSON array of tasks in {self.path!r}, "
                f"got {type(data).__name__}."
            )
        for index, item in enumerate(data):
            if not isinstance(item, dict) or "id" not in item or "description" not in item:
                raise StorageError(
                    f"Task entry {index} in {self.path!r} is malformed: "
                    "each task must be an object with at least 'id' and 'description'."
                )
        return data

    def save(self, tasks: list[Any]) -> None:
        """Write tasks to disk atomically.

        ``tasks`` may be :class:`~taskmanager.tasks.Task` objects (anything
        with a ``to_dict`` method) or plain dicts.
        """
        payload = [
            task.to_dict() if hasattr(task, "to_dict") else task for task in tasks
        ]
        tmp_path = self.path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
            os.replace(tmp_path, self.path)
        except OSError as exc:
            raise StorageError(
                f"Cannot write {self.path!r}: {exc}"
            ) from exc
