from __future__ import annotations

import argparse
import json
from typing import Any

from ..context import Context
from ..models import PRIORITIES, Task

NAME = "list"
HELP = "list tasks"


def add_parser(subparsers: Any) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(NAME, help=HELP, description=HELP)
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="include completed tasks",
    )
    parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        help="only show tasks with this priority",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    parser.set_defaults(func=run)
    return parser


def _matches(task: Task, args: argparse.Namespace) -> bool:
    if not args.all and task.done:
        return False
    if args.priority and task.priority != args.priority:
        return False
    return True


def run(args: argparse.Namespace, ctx: Context) -> int:
    tasks = [task for task in ctx.storage.load() if _matches(task, args)]
    if args.json:
        print(json.dumps([task.to_dict() for task in tasks], indent=2))
        return 0
    if not tasks:
        print("No tasks.")
        return 0
    for task in tasks:
        mark = "x" if task.done else " "
        due = f"  due {task.due}" if task.due else ""
        print(f"[{mark}] {task.id:>3}  {task.priority:<6}  {task.title}{due}")
    return 0
