"""``clitool done`` — mark a task complete."""

from __future__ import annotations

import argparse
import sys

from ..storage import Store


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "done",
        help="mark a task as completed",
        description="Mark the task with the given id as completed.",
    )
    parser.add_argument("id", type=int, help="task id")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, store: Store) -> int:
    task = store.mark_done(args.id)
    if task is None:
        print(f"error: no task with id {args.id}", file=sys.stderr)
        return 1
    print(f"Completed task {task.id}: {task.title}")
    return 0
