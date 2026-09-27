"""The ``config`` subcommand, which has nested subcommands of its own."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(
    os.environ.get("MYTOOL_CONFIG", "~/.config/mytool/config.json")
).expanduser()


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"mytool: cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"mytool: {path} does not contain a JSON object")
    return data


def _save(path: Path, data: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except OSError as exc:
        raise SystemExit(f"mytool: cannot write {path}: {exc}") from exc


def add_parser(subparsers, parents=()) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "config",
        parents=parents,
        help="view or edit stored settings",
        description="View or edit settings stored in a JSON file.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="config file location (default: %(default)s)",
    )
    parser.set_defaults(func=run)

    actions = parser.add_subparsers(
        dest="action",
        title="actions",
        metavar="<action>",
        required=True,
    )

    show = actions.add_parser("show", parents=parents, help="print the entire config")
    show.set_defaults(func=_run_show)

    get = actions.add_parser("get", parents=parents, help="print a single value")
    get.add_argument("key", help="setting name")
    get.set_defaults(func=_run_get)

    set_cmd = actions.add_parser("set", parents=parents, help="set a value")
    set_cmd.add_argument("key", help="setting name")
    set_cmd.add_argument("value", help="value to store")
    set_cmd.set_defaults(func=_run_set)

    unset = actions.add_parser("unset", parents=parents, help="remove a value")
    unset.add_argument("key", help="setting name")
    unset.set_defaults(func=_run_unset)

    return parser


def run(context) -> int:
    return int(context.args.func(context))


def _run_show(context) -> int:
    data = _load(context.args.file)
    if not context.quiet:
        print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def _run_get(context) -> int:
    data = _load(context.args.file)
    key = context.args.key
    if key not in data:
        print(f"mytool: no such key: {key}", file=sys.stderr)
        return 1
    if not context.quiet:
        print(data[key])
    return 0


def _run_set(context) -> int:
    args = context.args
    data = _load(args.file)
    data[args.key] = args.value
    _save(args.file, data)
    context.info(f"set {args.key!r} in {args.file}")
    return 0


def _run_unset(context) -> int:
    args = context.args
    data = _load(args.file)
    if args.key not in data:
        print(f"mytool: no such key: {args.key}", file=sys.stderr)
        return 1
    del data[args.key]
    _save(args.file, data)
    context.info(f"unset {args.key!r} in {args.file}")
    return 0
