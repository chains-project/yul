from __future__ import annotations

import argparse
import sys

_STORE = {"color": "auto", "region": "us-east-1"}


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("config", help="Inspect and modify configuration")
    actions = parser.add_subparsers(dest="action", metavar="ACTION")
    actions.required = True

    get_parser = actions.add_parser("get", help="Print a configuration value")
    get_parser.add_argument("key", help="configuration key to read")
    get_parser.set_defaults(handler=handle_get)

    set_parser = actions.add_parser("set", help="Set a configuration value")
    set_parser.add_argument("key", help="configuration key to write")
    set_parser.add_argument("value", help="value to store")
    set_parser.set_defaults(handler=handle_set)

    list_parser = actions.add_parser("list", help="List all configuration values")
    list_parser.set_defaults(handler=handle_list)


def handle_get(args: argparse.Namespace) -> int:
    if args.key not in _STORE:
        print(f"error: unknown key {args.key!r}", file=sys.stderr)
        return 1
    print(_STORE[args.key])
    return 0


def handle_set(args: argparse.Namespace) -> int:
    _STORE[args.key] = args.value
    if args.verbose:
        print(f"config: set {args.key!r}")
    return 0


def handle_list(args: argparse.Namespace) -> int:
    for key in sorted(_STORE):
        print(f"{key}={_STORE[key]}")
    return 0
