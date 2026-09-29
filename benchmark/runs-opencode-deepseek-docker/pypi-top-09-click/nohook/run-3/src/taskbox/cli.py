"""Command-line interface for taskbox.

The parser is a thin dispatch layer: every subcommand registers a handler via
``set_defaults(func=...)`` and ``main`` invokes it with the parsed namespace and
a :class:`~taskbox.storage.Store` instance.
"""

import argparse
import json
import sys
from collections import Counter

from taskbox import __version__
from taskbox.storage import Store, StoreError

PRIORITIES = ("low", "medium", "high")
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def build_parser():
    parser = argparse.ArgumentParser(
        prog="taskbox",
        description="A small command-line task manager.",
        epilog="Run 'taskbox COMMAND --help' for command-specific options.",
    )
    parser.add_argument(
        "--store",
        metavar="PATH",
        help="path to the task store (default: ~/.taskbox/tasks.json, env TASKBOX_STORE)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase output verbosity (repeatable)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command", metavar="COMMAND", required=True
    )

    add = subparsers.add_parser("add", help="add a new task")
    add.add_argument("title", help="task title")
    add.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        default="medium",
        help="task priority (default: medium)",
    )
    add.add_argument(
        "-t",
        "--tag",
        action="append",
        default=[],
        metavar="TAG",
        help="attach a tag (repeatable)",
    )
    add.add_argument("-d", "--due", metavar="DATE", help="due date, e.g. 2026-10-01")
    add.set_defaults(func=cmd_add)

    list_cmd = subparsers.add_parser(
        "list", aliases=["ls"], help="list tasks"
    )
    list_cmd.add_argument(
        "-s",
        "--status",
        choices=("all", "todo", "done"),
        default="all",
        help="filter by status (default: all)",
    )
    list_cmd.add_argument("-p", "--priority", choices=PRIORITIES, help="filter by priority")
    list_cmd.add_argument("-t", "--tag", metavar="TAG", help="filter by tag")
    list_cmd.add_argument("--json", action="store_true", help="emit JSON")
    list_cmd.set_defaults(func=cmd_list)

    done = subparsers.add_parser("done", help="mark tasks as done")
    done.add_argument("ids", nargs="+", type=int, metavar="ID")
    done.set_defaults(func=cmd_done)

    remove = subparsers.add_parser("remove", aliases=["rm"], help="delete tasks")
    remove.add_argument("ids", nargs="+", type=int, metavar="ID")
    remove.set_defaults(func=cmd_remove)

    show = subparsers.add_parser("show", help="show a single task")
    show.add_argument("id", type=int, metavar="ID")
    show.add_argument("--json", action="store_true", help="emit JSON")
    show.set_defaults(func=cmd_show)

    stats = subparsers.add_parser("stats", help="show task statistics")
    stats.add_argument("--json", action="store_true", help="emit JSON")
    stats.set_defaults(func=cmd_stats)

    return parser


def _find(tasks, task_id):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def cmd_add(args, store):
    tasks = store.load()
    task = {
        "id": store.next_id(tasks),
        "title": args.title,
        "priority": args.priority,
        "tags": list(args.tag),
        "due": args.due,
        "done": False,
    }
    tasks.append(task)
    store.save(tasks)
    print(f"added task #{task['id']}: {task['title']}")
    return 0


def cmd_list(args, store):
    tasks = store.load()
    if args.status == "todo":
        tasks = [task for task in tasks if not task.get("done")]
    elif args.status == "done":
        tasks = [task for task in tasks if task.get("done")]
    if args.priority:
        tasks = [task for task in tasks if task.get("priority") == args.priority]
    if args.tag:
        tasks = [task for task in tasks if args.tag in task.get("tags", [])]

    tasks.sort(
        key=lambda task: (
            task.get("done", False),
            PRIORITY_ORDER.get(task.get("priority"), 1),
            task.get("id", 0),
        )
    )

    if args.json:
        print(json.dumps(tasks, indent=2))
        return 0

    if not tasks:
        print("no tasks")
        return 0

    for task in tasks:
        mark = "x" if task.get("done") else " "
        tags = "".join(f" #{tag}" for tag in task.get("tags", []))
        due = f" (due {task['due']})" if task.get("due") else ""
        print(
            f"[{mark}] #{task['id']:<3} {task.get('priority', 'medium'):<6} "
            f"{task.get('title', '')}{tags}{due}"
        )
    return 0


def cmd_done(args, store):
    tasks = store.load()
    missing = [task_id for task_id in args.ids if _find(tasks, task_id) is None]
    if missing:
        return _missing_error(missing)
    for task_id in args.ids:
        _find(tasks, task_id)["done"] = True
    store.save(tasks)
    print(f"completed {len(args.ids)} task(s)")
    return 0


def cmd_remove(args, store):
    tasks = store.load()
    missing = [task_id for task_id in args.ids if _find(tasks, task_id) is None]
    if missing:
        return _missing_error(missing)
    remaining = [task for task in tasks if task.get("id") not in set(args.ids)]
    store.save(remaining)
    print(f"removed {len(args.ids)} task(s)")
    return 0


def cmd_show(args, store):
    task = _find(store.load(), args.id)
    if task is None:
        return _missing_error([args.id])
    if args.json:
        print(json.dumps(task, indent=2))
        return 0
    print(f"id:       {task.get('id')}")
    print(f"title:    {task.get('title')}")
    print(f"priority: {task.get('priority', 'medium')}")
    print(f"status:   {'done' if task.get('done') else 'todo'}")
    print(f"tags:     {', '.join(task.get('tags', [])) or '-'}")
    print(f"due:      {task.get('due') or '-'}")
    return 0


def cmd_stats(args, store):
    tasks = store.load()
    total = len(tasks)
    done = sum(1 for task in tasks if task.get("done"))
    counts = Counter(task.get("priority", "medium") for task in tasks)
    summary = {
        "total": total,
        "done": done,
        "todo": total - done,
        "by_priority": {name: counts.get(name, 0) for name in PRIORITIES},
    }
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    print(f"total: {summary['total']}")
    print(f"done:  {summary['done']}")
    print(f"todo:  {summary['todo']}")
    for name in PRIORITIES:
        print(f"{name:>6}: {summary['by_priority'][name]}")
    return 0


def _missing_error(ids):
    print(
        "error: no such task: " + ", ".join(str(task_id) for task_id in ids),
        file=sys.stderr,
    )
    return 1


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    store = Store(args.store)
    if args.verbose:
        print(f"using store: {store.path}", file=sys.stderr)
    try:
        return args.func(args, store)
    except StoreError as exc:
        parser.exit(1, f"error: {exc}\n")
