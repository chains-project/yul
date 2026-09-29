from __future__ import annotations

import argparse
from datetime import date
from typing import Any

from ..context import Context
from ..models import PRIORITIES, Task

NAME = "add"
HELP = "add a new task"


def parse_due(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date: {value!r} (expected YYYY-MM-DD)"
        ) from None


def add_parser(subparsers: Any) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(NAME, help=HELP, description=HELP)
    parser.add_argument("title", help="task description")
    parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        default="medium",
        help="task priority (default: medium)",
    )
    parser.add_argument(
        "-d",
        "--due",
        type=parse_due,
        metavar="DATE",
        help="due date in YYYY-MM-DD format",
    )
    parser.set_defaults(func=run)
    return parser


def run(args: argparse.Namespace, ctx: Context) -> int:
    tasks = ctx.storage.load()
    task = Task(
        id=ctx.storage.next_id(tasks),
        title=args.title,
        priority=args.priority,
        due=args.due,
    )
    tasks.append(task)
    ctx.storage.save(tasks)
    ctx.log(f"saved {len(tasks)} task(s) to {ctx.storage.path}")
    print(f"Added task {task.id}: {task.title}")
    return 0
