# Task Manager

A simple command-line task manager written in pure Python (standard library
only). Tasks are persisted to a JSON file so they survive between runs.

## Project layout

```
taskmanager/
    __init__.py     package exports
    cli.py          command-line interface (argparse)
    tasks.py        task model + management logic (TaskManager)
    storage.py      JSON file persistence (JsonStorage)
    __main__.py     enables `python -m taskmanager`
tests/
    test_taskmanager.py   unit tests (unittest)
```

## Requirements

- Python 3.10+ (no third-party dependencies)

## Usage

Run from this directory:

```bash
python -m taskmanager --file tasks.json add Buy groceries
python -m taskmanager --file tasks.json list
python -m taskmanager --file tasks.json complete 1
python -m taskmanager --file tasks.json delete 2
```

`--file` is optional; it defaults to `tasks.json` in the current directory.

### Commands

| Command    | Description                                  |
|------------|--------------------------------------------|
| `add`      | Add a task: `add <description...>`         |
| `list`     | List all tasks with ID, timestamp, status  |
| `complete` | Mark a task completed: `complete <id>`     |
| `delete`   | Delete a task: `delete <id>`               |

### Example session

```console
$ python -m taskmanager add Buy groceries
Added task #1: Buy groceries

$ python -m taskmanager add Write report
Added task #2: Write report

$ python -m taskmanager list
[ ] #1  2026-11-18T12:00:00+00:00  Buy groceries
[ ] #2  2026-11-18T12:00:05+00:00  Write report

$ python -m taskmanager complete 1
Completed task #1: Buy groceries

$ python -m taskmanager list
[x] #1  2026-11-18T12:00:00+00:00  Buy groceries
[ ] #2  2026-11-18T12:00:05+00:00  Write report

$ python -m taskmanager delete 2
Deleted task #2: Write report
```

### Task format (JSON)

Each task has a unique integer `id`, a `description`, an ISO 8601
`created_at` timestamp (UTC), and a `completed` flag:

```json
[
  {
    "id": 1,
    "description": "Buy groceries",
    "created_at": "2026-11-18T12:00:00+00:00",
    "completed": true
  }
]
```

IDs are never reused: a new task always gets `max(existing IDs) + 1`.

### Error handling

- **Invalid ID** (non-integer argument): rejected by argparse with usage help.
- **Missing ID** (task not found): `Error: No task with ID N.` and exit code 1.
- **Missing file**: treated as an empty task list (first run works out of the box).
- **Malformed file** (invalid JSON, non-array root, or task entries missing
  `id`/`description`): `Error: ...` and exit code 1; the file is left untouched.
- **Empty description**: rejected with `Error: Task description must not be empty.`

## Running the tests

From this directory:

```bash
python -m unittest discover -s tests -v
```
