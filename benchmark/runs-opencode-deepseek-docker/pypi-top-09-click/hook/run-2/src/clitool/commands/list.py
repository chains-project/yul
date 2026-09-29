"""``clitool list`` — show stored tasks."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from ..storage import Store, Task

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "list",
        help="list tasks",
        description="List tasks, optionally filtered and sorted.",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="include completed tasks",
    )
    parser.add_argument(
        "-s",
        "--status",
        choices=("open", "done"),
        help="only show tasks with this status",
    )
    parser.add_argument(
        "--sort",
        choices=("id", "priority", "title"),
        default="id",
        help="sort order (default: %(default)s)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    parser.set_defaults(func=run)


def _select(tasks: list[Task], args: argparse.Namespace) -> list[Task]:
    if args.status == "open":
        return [task for task in tasks if not task.done]
    if args.status == "done":
        return [task for task in tasks if task.done]
    if not args.all:
        return [task for task in tasks if not task.done]
    return tasks


def _sort(tasks: list[Task], key: str) -> list[Task]:
    if key == "priority":
        return sorted(tasks, key=lambda task: _PRIORITY_ORDER.get(task.priority, 99))
    if key == "title":
        return sorted(tasks, key=lambda task: task.title.lower())
    return sorted(tasks, key=lambda task: task.id)


def run(args: argparse.Namespace, store: Store) -> int:
    tasks = _sort(_select(store.load(), args), args.sort)

    if args.json:
        print(json.dumps([asdict(task) for task in tasks], indent=2))
        return 0

    if not tasks:
        print("No tasks.")
        return 0

    for task in tasks:
        mark = "x" if task.done else " "
        tags = f" [{', '.join(task.tags)}]" if task.tags else ""
        print(f"[{mark}] {task.id:>3}  {task.priority:<6}  {task.title}{tags}")
    return 0
