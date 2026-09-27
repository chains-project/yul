"""The ``greet`` subcommand."""

from __future__ import annotations

import argparse


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "greet",
        help="print a greeting",
        description="Print a greeting to NAME.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="who to greet (default: world)",
    )
    parser.add_argument(
        "-u",
        "--uppercase",
        action="store_true",
        help="shout the greeting",
    )
    parser.add_argument(
        "-r",
        "--repeat",
        type=positive_int,
        default=1,
        metavar="N",
        help="repeat the greeting N times (default: 1)",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    message = f"Hello, {args.name}!"
    if args.uppercase:
        message = message.upper()
    for _ in range(args.repeat):
        print(message)
    return 0
