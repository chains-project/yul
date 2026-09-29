"""The ``greet`` subcommand."""

from __future__ import annotations

import argparse


def register(subparsers: "argparse._SubParsersAction") -> None:
    parser = subparsers.add_parser(
        "greet",
        help="print a greeting",
        description="Print a personalized greeting one or more times.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="who to greet (default: world)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=positive_int,
        default=1,
        metavar="N",
        help="number of times to greet (default: 1)",
    )
    parser.add_argument(
        "-s",
        "--shout",
        action="store_true",
        help="uppercase the greeting",
    )
    parser.set_defaults(handler=run)


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value!r}")
    return number


def run(args: argparse.Namespace) -> int:
    message = f"Hello, {args.name}!"
    if args.shout:
        message = message.upper()
    for _ in range(args.count):
        print(message)
    return 0
