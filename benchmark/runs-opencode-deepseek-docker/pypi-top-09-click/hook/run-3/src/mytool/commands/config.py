"""The ``config`` subcommand.

Demonstrates a second level of subcommands (``config show``, ``config get``,
``config set``) backed by a small JSON file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG = Path("~/.config/mytool/config.json")


def config_path(args: argparse.Namespace) -> Path:
    """Resolve the config file location, honoring ``--config`` and the env."""
    if args.config:
        return Path(args.config)
    env = os.environ.get("MYTOOL_CONFIG")
    if env:
        return Path(env)
    return Path(os.path.expanduser(str(DEFAULT_CONFIG)))


def _load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"error: {path} does not contain a JSON object")
    return data


def _save(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def register(subparsers: "argparse._SubParsersAction") -> None:
    parser = subparsers.add_parser(
        "config",
        help="inspect and modify the configuration file",
        description="Read and write key/value pairs in the configuration file.",
    )
    actions = parser.add_subparsers(
        title="actions",
        dest="action",
        metavar="ACTION",
        required=True,
    )

    show = actions.add_parser("show", help="print the whole configuration")
    show.set_defaults(handler=run_show)

    get = actions.add_parser("get", help="print a single value")
    get.add_argument("key", help="the key to look up")
    get.set_defaults(handler=run_get)

    set_ = actions.add_parser("set", help="set a key to a value")
    set_.add_argument("key", help="the key to set")
    set_.add_argument("value", help="the value to store")
    set_.set_defaults(handler=run_set)


def run_show(args: argparse.Namespace) -> int:
    data = _load(config_path(args))
    if not data:
        print("(configuration is empty)")
        return 0
    for key in sorted(data):
        print(f"{key} = {data[key]}")
    return 0


def run_get(args: argparse.Namespace) -> int:
    data = _load(config_path(args))
    if args.key not in data:
        print(f"error: unknown key: {args.key}", file=sys.stderr)
        return 1
    print(data[args.key])
    return 0


def run_set(args: argparse.Namespace) -> int:
    path = config_path(args)
    data = _load(path)
    data[args.key] = args.value
    _save(path, data)
    print(f"{args.key} = {args.value}")
    return 0
