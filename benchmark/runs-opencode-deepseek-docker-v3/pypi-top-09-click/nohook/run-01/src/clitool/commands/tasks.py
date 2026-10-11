"""The ``tasks`` command group backed by a local JSON file."""

from __future__ import annotations

import argparse
import json
import logging
import uuid
from pathlib import Path
from typing import Any

from clitool.errors import CliError

log = logging.getLogger("clitool.tasks")

DEFAULT_TASKS_PATH = Path.home() / ".local" / "share" / "clitool" / "tasks.json"


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "tasks",
        help="manage a local task list",
        description="Add, list, complete and remove tasks stored in a JSON file.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=DEFAULT_TASKS_PATH,
        metavar="PATH",
        help="task store file (default: %(default)s)",
    )
    actions = parser.add_subparsers(
        dest="action",
        metavar="ACTION",
        required=True,
        title="actions",
    )

    add = actions.add_parser("add", help="add a task")
    add.add_argument("title", help="task description")
    add.add_argument(
        "-t",
        "--tag",
        action="append",
        default=[],
        metavar="TAG",
        help="attach a tag; may be repeated",
    )
    add.add_argument(
        "-p",
        "--priority",
        type=int,
        choices=range(1, 6),
        default=3,
        metavar="{1..5}",
        help="priority from 1 (highest) to 5 (lowest) (default: %(default)s)",
    )
    add.set_defaults(handler=_add)

    listing = actions.add_parser("list", help="list tasks")
    listing.add_argument("--tag", help="only show tasks carrying this tag")
    listing.add_argument(
        "--all",
        action="store_true",
        help="include completed tasks",
    )
    listing.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="emit machine-readable JSON",
    )
    listing.set_defaults(handler=_list)

    remove = actions.add_parser("remove", help="remove tasks by id")
    remove.add_argument("ids", nargs="+", metavar="ID", help="task id(s)")
    remove.set_defaults(handler=_remove)

    done = actions.add_parser("done", help="mark tasks as completed")
    done.add_argument("ids", nargs="+", metavar="ID", help="task id(s)")
    done.set_defaults(handler=_done)


def _load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CliError(f"could not read tasks from {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CliError(f"invalid JSON in task store {path}: {exc}") from exc
    if not isinstance(data, list):
        raise CliError(f"task store {path} must contain a JSON list")
    return data


def _save(path: Path, tasks: list[dict[str, Any]]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise CliError(f"could not write tasks to {path}: {exc}") from exc


def _ensure_exist(tasks: list[dict[str, Any]], ids: list[str]) -> None:
    known = {task["id"] for task in tasks}
    missing = sorted(set(ids) - known)
    if missing:
        raise CliError(f"unknown task id(s): {', '.join(missing)}")


def _add(args: argparse.Namespace) -> int:
    tasks = _load(args.file)
    task = {
        "id": uuid.uuid4().hex[:8],
        "title": args.title,
        "tags": list(args.tag),
        "priority": args.priority,
        "done": False,
    }
    tasks.append(task)
    _save(args.file, tasks)
    print(f"added {task['id']}: {task['title']}")
    return 0


def _list(args: argparse.Namespace) -> int:
    tasks = _load(args.file)
    if not args.all:
        tasks = [task for task in tasks if not task.get("done")]
    if args.tag:
        tasks = [task for task in tasks if args.tag in task.get("tags", [])]
    tasks.sort(
        key=lambda task: (
            task.get("done", False),
            task.get("priority", 3),
            task.get("title", ""),
        )
    )

    if args.as_json:
        print(json.dumps(tasks, indent=2))
        return 0

    if not tasks:
        print("no tasks")
        return 0

    for task in tasks:
        status = "x" if task.get("done") else " "
        tags = task.get("tags") or []
        suffix = f" [{' '.join(tags)}]" if tags else ""
        print(
            f"[{status}] {task['id']} p{task.get('priority', 3)} "
            f"{task['title']}{suffix}"
        )
    return 0


def _remove(args: argparse.Namespace) -> int:
    tasks = _load(args.file)
    _ensure_exist(tasks, args.ids)
    selected = set(args.ids)
    remaining = [task for task in tasks if task["id"] not in selected]
    _save(args.file, remaining)
    print(f"removed {len(tasks) - len(remaining)} task(s)")
    return 0


def _done(args: argparse.Namespace) -> int:
    tasks = _load(args.file)
    _ensure_exist(tasks, args.ids)
    selected = set(args.ids)
    for task in tasks:
        if task["id"] in selected:
            task["done"] = True
    _save(args.file, tasks)
    print(f"completed {len(selected)} task(s)")
    return 0
