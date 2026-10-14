"""``mytool config``: nested subcommands backed by a JSON file."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from mytool.errors import CLIError


def default_config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "mytool" / "config.json"


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("config", help="read and write settings")
    p.add_argument(
        "--file", type=Path, default=None, metavar="PATH",
        help="config file (default: $XDG_CONFIG_HOME/mytool/config.json)",
    )
    actions = p.add_subparsers(
        title="actions", dest="action", metavar="<action>", required=True
    )

    get = actions.add_parser("get", help="print a value")
    get.add_argument("key")
    get.set_defaults(func=run_get)

    set_ = actions.add_parser("set", help="set a value")
    set_.add_argument("key")
    set_.add_argument("value")
    set_.set_defaults(func=run_set)

    unset = actions.add_parser("unset", help="remove a value")
    unset.add_argument("key")
    unset.set_defaults(func=run_unset)

    list_ = actions.add_parser("list", help="print all values")
    list_.set_defaults(func=run_list)


def _path(args: argparse.Namespace) -> Path:
    return args.file or default_config_path()


def load(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CLIError(f"invalid config file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CLIError(f"invalid config file {path}: expected a JSON object")
    return data


def save(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def run_get(args: argparse.Namespace) -> int:
    data = load(_path(args))
    if args.key not in data:
        raise CLIError(f"key not found: {args.key}")
    print(data[args.key])
    return 0


def run_set(args: argparse.Namespace) -> int:
    path = _path(args)
    data = load(path)
    data[args.key] = args.value
    save(path, data)
    return 0


def run_unset(args: argparse.Namespace) -> int:
    path = _path(args)
    data = load(path)
    if args.key not in data:
        raise CLIError(f"key not found: {args.key}")
    del data[args.key]
    save(path, data)
    return 0


def run_list(args: argparse.Namespace) -> int:
    for key, value in sorted(load(_path(args)).items()):
        print(f"{key}={value}")
    return 0
