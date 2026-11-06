#!/usr/bin/env python3
"""Task Tracker CLI: manage a to-do list from the terminal."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DB = Path.home() / ".task_tracker.json"
PRIORITIES = ("low", "medium", "high")


def load_tasks(db: Path) -> list:
    """Load tasks from the JSON file, returning an empty list if it doesn't exist."""
    if not db.exists():
        return []
    return json.loads(db.read_text(encoding="utf-8"))


def save_tasks(db: Path, tasks: list) -> None:
    db.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add_task(tasks: list, title: str, priority: str = "medium") -> dict:
    if not title.strip():
        raise ValueError("Title cannot be empty")
    if priority not in PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}")
    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {
        "id": next_id,
        "title": title.strip(),
        "priority": priority,
        "done": False,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    tasks.append(task)
    return task


def complete_task(tasks: list, task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return task
    raise KeyError(f"No task with id {task_id}")


def remove_task(tasks: list, task_id: int) -> dict:
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            return tasks.pop(index)
    raise KeyError(f"No task with id {task_id}")


def format_tasks(tasks: list, show_done: bool = True) -> str:
    rows = [t for t in tasks if show_done or not t["done"]]
    if not rows:
        return "No tasks."
    order = {"high": 0, "medium": 1, "low": 2}
    rows.sort(key=lambda t: (t["done"], order[t["priority"]], t["id"]))
    lines = []
    for t in rows:
        mark = "x" if t["done"] else " "
        lines.append(f"[{mark}] {t['id']:>3}  ({t['priority']:<6})  {t['title']}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A simple command-line task tracker.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="path to the JSON data file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title")
    p_add.add_argument("-p", "--priority", choices=PRIORITIES, default="medium")

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--pending", action="store_true", help="hide completed tasks")

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("id", type=int)

    p_rm = sub.add_parser("remove", help="delete a task")
    p_rm.add_argument("id", type=int)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    tasks = load_tasks(args.db)
    try:
        if args.command == "add":
            task = add_task(tasks, args.title, args.priority)
            print(f"Added task {task['id']}: {task['title']}")
        elif args.command == "list":
            print(format_tasks(tasks, show_done=not args.pending))
            return 0
        elif args.command == "done":
            task = complete_task(tasks, args.id)
            print(f"Completed task {task['id']}: {task['title']}")
        elif args.command == "remove":
            task = remove_task(tasks, args.id)
            print(f"Removed task {task['id']}: {task['title']}")
    except (KeyError, ValueError) as err:
        print(f"Error: {err.args[0]}", file=sys.stderr)
        return 1
    save_tasks(args.db, tasks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
