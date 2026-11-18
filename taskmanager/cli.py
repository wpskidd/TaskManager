"""Command-line interface for the task manager.

Usage:
    python -m taskmanager [--file PATH] add DESCRIPTION...
    python -m taskmanager [--file PATH] list
    python -m taskmanager [--file PATH] complete ID
    python -m taskmanager [--file PATH] delete ID
"""

from __future__ import annotations

import argparse
import sys

from .storage import JsonStorage, StorageError
from .tasks import TaskError, TaskManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskmanager",
        description="A simple command-line task manager.",
    )
    parser.add_argument(
        "--file",
        default="tasks.json",
        help="Path to the JSON file used for persistence (default: tasks.json).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a new task.")
    p_add.add_argument("description", nargs="+", help="Task description.")

    subparsers.add_parser("list", help="List all tasks.")

    p_complete = subparsers.add_parser("complete", help="Mark a task as completed.")
    p_complete.add_argument("id", type=int, help="ID of the task to complete.")

    p_delete = subparsers.add_parser("delete", help="Delete a task.")
    p_delete.add_argument("id", type=int, help="ID of the task to delete.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns a process exit code (0 = success)."""
    args = build_parser().parse_args(argv)

    try:
        manager = TaskManager(JsonStorage(args.file))
    except StorageError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        if args.command == "add":
            task = manager.add(" ".join(args.description))
            print(f"Added task #{task.id}: {task.description}")
        elif args.command == "list":
            tasks = manager.list()
            if not tasks:
                print("No tasks.")
            else:
                for task in tasks:
                    mark = "x" if task.completed else " "
                    print(f"[{mark}] #{task.id}  {task.created_at}  {task.description}")
        elif args.command == "complete":
            task = manager.complete(args.id)
            print(f"Completed task #{task.id}: {task.description}")
        elif args.command == "delete":
            task = manager.delete(args.id)
            print(f"Deleted task #{task.id}: {task.description}")
        else:  # pragma: no cover - argparse guarantees a known command
            return 2
    except TaskError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
