"""The ``config`` command group: dotted-key access to the JSON config."""

from __future__ import annotations

import argparse
import json
from typing import Any

from clitool.config import load_config, save_config
from clitool.errors import CliError


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "config",
        help="read and write tool configuration",
        description="Read and write the tool configuration using dotted keys.",
    )
    actions = parser.add_subparsers(
        dest="action",
        metavar="ACTION",
        required=True,
        title="actions",
    )

    listing = actions.add_parser("list", help="list all configuration values")
    listing.set_defaults(handler=_list)

    get = actions.add_parser("get", help="print a configuration value")
    get.add_argument("key", help="dotted key, for example 'user.name'")
    get.set_defaults(handler=_get)

    set_value = actions.add_parser("set", help="set a configuration value")
    set_value.add_argument("key", help="dotted key")
    set_value.add_argument("value", help="JSON value or plain string")
    set_value.set_defaults(handler=_set)

    unset = actions.add_parser("unset", help="remove a configuration value")
    unset.add_argument("key", help="dotted key")
    unset.set_defaults(handler=_unset)


def _get_nested(data: dict[str, Any], key: str) -> Any:
    node: Any = data
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise CliError(f"no such config key: {key}")
        node = node[part]
    return node


def _set_nested(data: dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".")
    node = data
    for part in parts[:-1]:
        child = node.setdefault(part, {})
        if not isinstance(child, dict):
            raise CliError(f"cannot set {key}: '{part}' is not a section")
        node = child
    node[parts[-1]] = value


def _del_nested(data: dict[str, Any], key: str) -> None:
    parts = key.split(".")
    node: Any = data
    for part in parts[:-1]:
        node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, dict):
            raise CliError(f"no such config key: {key}")
    if parts[-1] not in node:
        raise CliError(f"no such config key: {key}")
    del node[parts[-1]]


def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _list(args: argparse.Namespace) -> int:
    print(json.dumps(load_config(args.config), indent=2, sort_keys=True))
    return 0


def _get(args: argparse.Namespace) -> int:
    value = _get_nested(load_config(args.config), args.key)
    print(value if isinstance(value, str) else json.dumps(value))
    return 0


def _set(args: argparse.Namespace) -> int:
    data = load_config(args.config)
    _set_nested(data, args.key, _parse_value(args.value))
    save_config(args.config, data)
    return 0


def _unset(args: argparse.Namespace) -> int:
    data = load_config(args.config)
    _del_nested(data, args.key)
    save_config(args.config, data)
    return 0
