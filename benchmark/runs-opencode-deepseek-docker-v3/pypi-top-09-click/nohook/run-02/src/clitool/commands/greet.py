"""The ``greet`` subcommand."""

from __future__ import annotations

import argparse

NAME = "greet"
HELP = "Print a greeting."


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="who to greet (default: %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="repeat the greeting N times (default: %(default)s)",
    )
    parser.add_argument(
        "-u",
        "--uppercase",
        action="store_true",
        help="shout the greeting",
    )


def run(args: argparse.Namespace) -> int:
    if args.count < 1:
        print("error: --count must be a positive integer")
        return 2
    message = f"Hello, {args.name}!"
    if args.uppercase:
        message = message.upper()
    for _ in range(args.count):
        print(message)
    return 0
