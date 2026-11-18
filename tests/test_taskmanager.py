"""Automated tests for the task manager.

Run from the project root with:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from taskmanager.storage import JsonStorage, StorageError
from taskmanager.tasks import (
    InvalidTaskError,
    Task,
    TaskManager,
    TaskNotFoundError,
)


class TaskManagerTestCase(unittest.TestCase):
    """Tests for the task management logic and JSON persistence."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.path = os.path.join(self._tmpdir.name, "tasks.json")
        self.manager = TaskManager(JsonStorage(self.path))

    # -- add ---------------------------------------------------------------

    def test_add_creates_task_with_unique_ids_and_timestamp(self) -> None:
        first = self.manager.add("write tests")
        second = self.manager.add("ship it")

        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)
        self.assertEqual(first.description, "write tests")
        self.assertFalse(first.completed)
        self.assertTrue(first.created_at)  # ISO 8601 timestamp is set
        self.assertEqual(self.manager.list(), [first, second])

    def test_add_rejects_empty_description(self) -> None:
        with self.assertRaises(InvalidTaskError):
            self.manager.add("   ")
        self.assertEqual(self.manager.list(), [])

    # -- list / get --------------------------------------------------------

    def test_list_is_empty_initially(self) -> None:
        self.assertEqual(self.manager.list(), [])

    def test_get_returns_task_and_missing_id_raises(self) -> None:
        task = self.manager.add("buy milk")
        self.assertIs(self.manager.get(1), task)
        with self.assertRaises(TaskNotFoundError):
            self.manager.get(99)

    # -- complete ------------------------------------------------------------

    def test_complete_marks_task_completed(self) -> None:
        task = self.manager.add("buy milk")
        completed = self.manager.complete(1)
        self.assertTrue(completed.completed)
        self.assertIs(self.manager.get(1), completed)

    def test_complete_missing_id_raises(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete(42)

    # -- delete --------------------------------------------------------------

    def test_delete_removes_task(self) -> None:
        self.manager.add("first")
        self.manager.add("second")
        self.manager.delete(1)
        remaining = self.manager.list()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].description, "second")

    def test_delete_missing_id_raises(self) -> None:
        with self.assertRaises(TaskNotFoundError):
            self.manager.delete(7)

    # -- persistence ---------------------------------------------------------

    def test_tasks_survive_between_runs(self) -> None:
        self.manager.add("remembered task")
        self.manager.complete(1)

        # Simulate a new program run: a fresh manager over the same file.
        reopened = TaskManager(JsonStorage(self.path))
        tasks = reopened.list()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "remembered task")
        self.assertTrue(tasks[0].completed)
        self.assertEqual(tasks[0].id, 1)

    def test_new_manager_continues_ids_after_delete(self) -> None:
        self.manager.add("a")
        self.manager.add("b")
        self.manager.delete(1)
        task = self.manager.add("c")
        self.assertEqual(task.id, 3)  # never reuses a deleted ID

    def test_missing_file_is_treated_as_empty(self) -> None:
        missing = os.path.join(self._tmpdir.name, "does-not-exist.json")
        self.assertEqual(JsonStorage(missing).load(), [])

    # -- malformed input ------------------------------------------------------

    def test_malformed_json_raises_storage_error(self) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{ this is not json")
        with self.assertRaises(StorageError):
            TaskManager(JsonStorage(self.path))

    def test_non_list_json_raises_storage_error(self) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump({"id": 1, "description": "not a list"}, handle)
        with self.assertRaises(StorageError):
            TaskManager(JsonStorage(self.path))

    def test_malformed_task_entry_raises_storage_error(self) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump([{"nope": True}], handle)
        with self.assertRaises(StorageError):
            TaskManager(JsonStorage(self.path))

    # -- storage round-trip ----------------------------------------------------

    def test_storage_round_trip_preserves_fields(self) -> None:
        task = Task(id=5, description="round trip", created_at="2026-01-01T00:00:00+00:00")
        storage = JsonStorage(self.path)
        storage.save([task])
        loaded = JsonStorage(self.path).load()
        self.assertEqual(loaded, [task.to_dict()])


if __name__ == "__main__":
    unittest.main()
