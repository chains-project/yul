"""The ``config`` subcommand: inspect and edit a small JSON settings store."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

NAME = "config"
HELP = "Get, set, or list configuration values."

DEFAULT_STORE = Path.home() / ".clitool.json"


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=DEFAULT_STORE,
        help="path to the config file (default: %(default)s)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--list", action="store_true", help="list all values")
    group.add_argument("-g", "--get", metavar="KEY", help="print the value for KEY")
    group.add_argument("-s", "--set", nargs=2, metavar=("KEY", "VALUE"), help="store KEY = VALUE")


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def run(args: argparse.Namespace) -> int:
    data = _load(args.file)

    if args.set:
        key, value = args.set
        data[key] = value
        _save(args.file, data)
        print(f"{key} = {value}")
        return 0

    if args.get:
        if args.get not in data:
            print(f"error: no such key: {args.get}")
            return 1
        print(data[args.get])
        return 0

    if args.list or not data:
        for key in sorted(data):
            print(f"{key} = {data[key]}")
        return 0

    return 0
