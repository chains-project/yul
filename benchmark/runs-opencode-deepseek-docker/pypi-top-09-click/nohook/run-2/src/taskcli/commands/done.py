from __future__ import annotations

import argparse
import sys
from typing import Any

from ..context import Context
from ._common import find_task, positive_int

NAME = "done"
HELP = "mark a task as completed"


def add_parser(subparsers: Any) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(NAME, help=HELP, description=HELP)
    parser.add_argument("id", type=positive_int, help="task id")
    parser.add_argument(
        "--undo",
        action="store_true",
        help="mark the task as not completed instead",
    )
    parser.set_defaults(func=run)
    return parser


def run(args: argparse.Namespace, ctx: Context) -> int:
    tasks = ctx.storage.load()
    try:
        task = find_task(tasks, args.id)
    except LookupError as exc:
        print(f"task: error: {exc}", file=sys.stderr)
        return 1
    task.done = not args.undo
    ctx.storage.save(tasks)
    state = "reopened" if args.undo else "completed"
    print(f"Task {task.id} {state}: {task.title}")
    return 0
