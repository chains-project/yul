"""The ``config`` subcommand: nested subcommands that persist state to a JSON file."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(
    os.environ.get("CLITOOL_CONFIG", "~/.config/clitool/config.json")
).expanduser()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("could not read config %s: %s", path, exc)
        return {}
    if not isinstance(data, dict):
        logger.error("config %s does not contain a JSON object", path)
        return {}
    return data


def _save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "config",
        help="Read and write configuration values.",
        description="Read and write configuration values stored in a JSON file.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the config file (default: %(default)s).",
    )
    config_subparsers = parser.add_subparsers(
        title="commands",
        dest="config_command",
        metavar="COMMAND",
        required=True,
    )

    get = config_subparsers.add_parser("get", help="Print a value.")
    get.add_argument("key", help="Key to read.")
    get.set_defaults(handler=_run_get)

    set_ = config_subparsers.add_parser("set", help="Set a value.")
    set_.add_argument("key", help="Key to write.")
    set_.add_argument("value", help="Value to store.")
    set_.set_defaults(handler=_run_set)

    unset = config_subparsers.add_parser("unset", help="Remove a value.")
    unset.add_argument("key", help="Key to remove.")
    unset.set_defaults(handler=_run_unset)

    list_ = config_subparsers.add_parser("list", help="List all values.")
    list_.set_defaults(handler=_run_list)


def _run_get(args: argparse.Namespace) -> int:
    data = _load(args.file)
    if args.key not in data:
        logger.error("key not found: %s", args.key)
        return 1
    print(data[args.key])
    return 0


def _run_set(args: argparse.Namespace) -> int:
    data = _load(args.file)
    data[args.key] = args.value
    _save(args.file, data)
    return 0


def _run_unset(args: argparse.Namespace) -> int:
    data = _load(args.file)
    if args.key not in data:
        logger.error("key not found: %s", args.key)
        return 1
    del data[args.key]
    _save(args.file, data)
    return 0


def _run_list(args: argparse.Namespace) -> int:
    data = _load(args.file)
    for key in sorted(data):
        print(f"{key}={data[key]}")
    return 0
