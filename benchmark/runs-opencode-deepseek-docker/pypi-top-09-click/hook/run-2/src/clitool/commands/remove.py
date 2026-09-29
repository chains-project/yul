"""``clitool remove`` — delete a task."""

from __future__ import annotations

import argparse
import sys

from ..storage import Store


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "remove",
        help="remove a task",
        description="Remove the task with the given id.",
    )
    parser.add_argument("id", type=int, help="task id")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="report what would be removed without changing anything",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, store: Store) -> int:
    task = store.get(args.id)
    if task is None:
        print(f"error: no task with id {args.id}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Would remove task {task.id}: {task.title}")
        return 0

    store.remove(args.id)
    print(f"Removed task {task.id}: {task.title}")
    return 0
