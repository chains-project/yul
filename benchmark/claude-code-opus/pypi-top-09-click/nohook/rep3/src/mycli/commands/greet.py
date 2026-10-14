"""``mycli greet``: print a greeting."""

from __future__ import annotations

import argparse


def positive_int(value: str) -> int:
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError(f"must be >= 1, got {n}")
    return n


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("greet", help="print a greeting", description="Print a greeting.")
    p.add_argument("name", help="who to greet")
    p.add_argument("-g", "--greeting", default="Hello", help="greeting word (default: %(default)s)")
    p.add_argument("-n", "--times", type=positive_int, default=1, help="repeat N times")
    p.add_argument("--shout", action="store_true", help="print in uppercase")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    message = f"{args.greeting}, {args.name}!"
    if args.shout:
        message = message.upper()
    for _ in range(args.times):
        print(message)
    return 0
