"""The ``greet`` subcommand."""

from __future__ import annotations

import argparse


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid integer value: {value!r}")
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def add_parser(subparsers, parents=()) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "greet",
        parents=parents,
        help="print a greeting",
        description="Print a greeting one or more times.",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="world",
        help="who to greet (default: %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=_positive_int,
        default=1,
        help="number of times to repeat the greeting (default: %(default)s)",
    )
    parser.add_argument(
        "--greeting",
        default="Hello",
        help="greeting word to use (default: %(default)s)",
    )
    parser.add_argument(
        "--shout",
        action="store_true",
        help="convert the greeting to uppercase",
    )
    parser.set_defaults(func=run)
    return parser


def run(context) -> int:
    args = context.args
    message = f"{args.greeting}, {args.name}!"
    if args.shout:
        message = message.upper()

    context.info(f"greeting {args.name!r} {args.count} time(s)")
    if not context.quiet:
        for _ in range(args.count):
            print(message)
    return 0
