"""The ``config`` subcommand with nested get/set/list actions."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def config_path() -> Path:
    """Location of the JSON config file, honouring XDG and an override."""
    override = os.environ.get("MYTOOL_CONFIG_DIR")
    if override:
        return Path(override) / "config.json"
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / "mytool" / "config.json"


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save(path: Path, values: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(values, handle, indent=2, sort_keys=True)
        handle.write("\n")


def register(
    subparsers: argparse._SubParsersAction,
    common: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "config",
        parents=[common],
        help="read and write configuration values",
        description="Manage persistent configuration stored as JSON.",
    )
    actions = parser.add_subparsers(
        dest="config_action",
        metavar="ACTION",
        title="actions",
    )

    get = actions.add_parser("get", parents=[common], help="print the value for KEY")
    get.add_argument("key")
    get.set_defaults(func=run_get)

    set_ = actions.add_parser(
        "set", parents=[common], help="store VALUE under KEY"
    )
    set_.add_argument("key")
    set_.add_argument("value")
    set_.set_defaults(func=run_set)

    listing = actions.add_parser(
        "list", parents=[common], help="list all stored values"
    )
    listing.set_defaults(func=run_list)

    parser.set_defaults(func=lambda args: _usage(parser))


def _usage(parser: argparse.ArgumentParser) -> int:
    parser.print_help()
    return 2


def run_get(args: argparse.Namespace) -> int:
    values = load(config_path())
    if args.key not in values:
        print(f"error: no such key: {args.key}")
        return 1
    print(values[args.key])
    return 0


def run_set(args: argparse.Namespace) -> int:
    path = config_path()
    values = load(path)
    values[args.key] = args.value
    save(path, values)
    if args.verbose:
        print(f"saved {args.key} to {path}")
    return 0


def run_list(args: argparse.Namespace) -> int:
    values = load(config_path())
    for key in sorted(values):
        print(f"{key}={values[key]}")
    return 0
