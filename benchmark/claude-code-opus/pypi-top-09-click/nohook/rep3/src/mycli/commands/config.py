"""``mycli config``: read and write settings (nested subcommands)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mycli.errors import CLIError


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "config", help="manage settings", description="Read and write settings."
    )
    sub = p.add_subparsers(dest="config_command", metavar="ACTION", required=True)

    get = sub.add_parser("get", help="print a setting")
    get.add_argument("key")
    get.set_defaults(func=run_get)

    set_ = sub.add_parser("set", help="change a setting")
    set_.add_argument("key")
    set_.add_argument("value")
    set_.set_defaults(func=run_set)

    unset = sub.add_parser("unset", help="remove a setting")
    unset.add_argument("key")
    unset.set_defaults(func=run_unset)

    list_ = sub.add_parser("list", help="print all settings")
    list_.add_argument("--json", action="store_true", help="output as JSON")
    list_.set_defaults(func=run_list)


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
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_get(args: argparse.Namespace) -> int:
    data = load(args.config)
    if args.key not in data:
        raise CLIError(f"no such key: {args.key}")
    print(data[args.key])
    return 0


def run_set(args: argparse.Namespace) -> int:
    data = load(args.config)
    data[args.key] = args.value
    save(args.config, data)
    return 0


def run_unset(args: argparse.Namespace) -> int:
    data = load(args.config)
    if data.pop(args.key, None) is None:
        raise CLIError(f"no such key: {args.key}")
    save(args.config, data)
    return 0


def run_list(args: argparse.Namespace) -> int:
    data = load(args.config)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        for key, value in sorted(data.items()):
            print(f"{key}={value}")
    return 0
