"""Command-line interface: argument parsing and subcommand handlers."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from todo_cli import __version__
from todo_cli.store import PRIORITIES, Item, Store, default_path

PRIORITY_ORDER = {p: n for n, p in enumerate(PRIORITIES)}


class CLIError(Exception):
    """An expected, user-facing error; printed without a traceback."""


# --- subcommand handlers -----------------------------------------------------
# Each handler receives the parsed namespace and an open Store, and returns an
# exit code.


def cmd_add(args: argparse.Namespace, store: Store) -> int:
    text = " ".join(args.text).strip()
    if not text:
        raise CLIError("todo text must not be empty")
    item = store.add(text, priority=args.priority, tags=args.tag)
    store.save()
    if not args.quiet:
        print(f"Added #{item.id}: {item.text}")
    return 0


def cmd_list(args: argparse.Namespace, store: Store) -> int:
    items = store.items
    if not args.all:
        items = [i for i in items if not i.done]
    if args.tag:
        items = [i for i in items if args.tag in i.tags]
    if args.priority:
        items = [i for i in items if i.priority == args.priority]

    if args.sort == "priority":
        items = sorted(items, key=lambda i: -PRIORITY_ORDER[i.priority])
    elif args.sort == "created":
        items = sorted(items, key=lambda i: i.created)

    if args.format == "json":
        print(json.dumps([asdict(i) for i in items], indent=2))
        return 0

    if not items:
        if not args.quiet:
            print("No todos.")
        return 0
    for i in items:
        mark = "x" if i.done else " "
        tags = f"  [{', '.join(i.tags)}]" if i.tags else ""
        prio = "" if i.priority == "normal" else f" ({i.priority})"
        print(f"[{mark}] #{i.id:<3} {i.text}{prio}{tags}")
    return 0


def cmd_done(args: argparse.Namespace, store: Store) -> int:
    for item_id in args.ids:
        item = _get(store, item_id)
        item.done = not args.undo
        if not args.quiet:
            state = "Reopened" if args.undo else "Completed"
            print(f"{state} #{item.id}: {item.text}")
    store.save()
    return 0


def cmd_remove(args: argparse.Namespace, store: Store) -> int:
    items = [_get(store, i) for i in args.ids]
    if not args.yes and sys.stdin.isatty():
        answer = input(f"Remove {len(items)} item(s)? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Aborted.")
            return 1
    for item in items:
        store.remove(item.id)
        if not args.quiet:
            print(f"Removed #{item.id}: {item.text}")
    store.save()
    return 0


def cmd_clear(args: argparse.Namespace, store: Store) -> int:
    before = len(store.items)
    store.items = [i for i in store.items if not i.done]
    removed = before - len(store.items)
    if args.dry_run:
        print(f"Would remove {removed} completed item(s).")
        return 0
    store.save()
    if not args.quiet:
        print(f"Removed {removed} completed item(s).")
    return 0


def _get(store: Store, item_id: int) -> Item:
    try:
        return store.get(item_id)
    except KeyError:
        raise CLIError(f"no todo with id #{item_id}") from None


# --- argument parsing --------------------------------------------------------


def positive_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid id: {value!r}") from None
    if n < 1:
        raise argparse.ArgumentTypeError(f"id must be >= 1, got {n}")
    return n


def build_parser() -> argparse.ArgumentParser:
    # Options shared by every subcommand, so they work before *or* after it:
    #   todo -q add milk    and    todo add milk -q
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-f",
        "--file",
        type=Path,
        default=argparse.SUPPRESS,
        help="path to the todo store (default: $TODO_FILE or ~/.todo.json)",
    )
    common.add_argument(
        "-q", "--quiet", action="store_true", default=argparse.SUPPRESS, help="suppress output"
    )

    parser = argparse.ArgumentParser(
        prog="todo",
        description="Manage a simple todo list from the command line.",
        parents=[common],
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    p = sub.add_parser("add", parents=[common], help="add a new todo")
    p.add_argument("text", nargs="+", help="todo text")
    p.add_argument("-p", "--priority", choices=PRIORITIES, default="normal")
    p.add_argument("-t", "--tag", action="append", default=[], help="tag the item (repeatable)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", aliases=["ls"], parents=[common], help="list todos")
    p.add_argument("-a", "--all", action="store_true", help="include completed items")
    p.add_argument("-t", "--tag", help="only show items with this tag")
    p.add_argument("-p", "--priority", choices=PRIORITIES, help="only show this priority")
    p.add_argument("-s", "--sort", choices=("id", "priority", "created"), default="id")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("done", parents=[common], help="mark todos as completed")
    p.add_argument("ids", nargs="+", type=positive_int, metavar="ID")
    p.add_argument("-u", "--undo", action="store_true", help="mark as not completed instead")
    p.set_defaults(func=cmd_done)

    p = sub.add_parser("remove", aliases=["rm"], parents=[common], help="delete todos")
    p.add_argument("ids", nargs="+", type=positive_int, metavar="ID")
    p.add_argument("-y", "--yes", action="store_true", help="don't ask for confirmation")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("clear", parents=[common], help="delete all completed todos")
    p.add_argument("-n", "--dry-run", action="store_true", help="show what would be removed")
    p.set_defaults(func=cmd_clear)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.quiet = getattr(args, "quiet", False)
    path = getattr(args, "file", None) or default_path()

    try:
        store = Store(path)
    except (OSError, ValueError, TypeError) as e:
        print(f"todo: error: could not read store {path}: {e}", file=sys.stderr)
        return 1

    try:
        return args.func(args, store)
    except CLIError as e:
        print(f"todo: error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"todo: error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
