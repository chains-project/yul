"""Print a greeting."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("greet", help="print a greeting", description=__doc__)
    parser.add_argument("name", nargs="?", default="world", help="who to greet (default: world)")
    parser.add_argument(
        "-n", "--times", type=_positive_int, default=1, metavar="N", help="repeat N times"
    )
    parser.add_argument("--shout", action="store_true", help="print in upper case")
    parser.add_argument("--greeting", default="Hello", help="greeting word (default: Hello)")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    message = f"{args.greeting}, {args.name}!"
    if args.shout:
        message = message.upper()
    for _ in range(args.times):
        print(message)
    return 0


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid integer: {value!r}") from None
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be >= 1, got {number}")
    return number
