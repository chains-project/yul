"""``clitool add`` — create a task."""

from __future__ import annotations

import argparse

from ..storage import PRIORITIES, Store


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "add",
        help="add a new task",
        description="Add a new task to the store.",
    )
    parser.add_argument("title", help="task description")
    parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        default="medium",
        help="task priority (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="append",
        dest="tags",
        default=[],
        metavar="TAG",
        help="attach a tag (repeatable)",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, store: Store) -> int:
    task = store.add(args.title, priority=args.priority, tags=args.tags)
    print(f"Added task {task.id}: {task.title}")
    return 0
