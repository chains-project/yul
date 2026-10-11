"""The ``greet`` subcommand."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "greet",
        help="Greet someone.",
        description="Print a greeting, optionally repeated and uppercased.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="who to greet (default: %(default)s)",
    )
    parser.add_argument(
        "-g",
        "--greeting",
        default="Hello",
        help="greeting word to use (default: %(default)s)",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="number of times to repeat the greeting (default: %(default)s)",
    )
    parser.add_argument(
        "-u",
        "--uppercase",
        action="store_true",
        help="uppercase the greeting",
    )
    parser.set_defaults(func=run)
    return parser


def run(args: argparse.Namespace) -> int:
    if args.count < 1:
        raise SystemExit("error: --count must be at least 1")

    message = f"{args.greeting}, {args.name}!"
    if args.uppercase:
        message = message.upper()

    for _ in range(args.count):
        print(message)
    return 0
