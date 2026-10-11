"""The ``greet`` subcommand."""

from __future__ import annotations

import argparse


def positive_int(value: str) -> int:
    """argparse type that accepts only integers greater than zero."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def register(
    subparsers: argparse._SubParsersAction,
    common: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        "greet",
        parents=[common],
        help="print a greeting",
        description="Print a greeting to the given name.",
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
    if args.verbose:
        print(f"greeting {args.name!r}, repeat={args.repeat}")
    for _ in range(args.repeat):
        print(message)
    return 0
