"""``mycli greet``: print a greeting."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("greet", help="print a greeting", description=__doc__)
    parser.add_argument("name", nargs="+", help="one or more names to greet")
    parser.add_argument("-g", "--greeting", default="Hello", help="greeting word (default: %(default)s)")
    parser.add_argument("-n", "--times", type=int, default=1, metavar="N", help="repeat N times")
    parser.add_argument("--shout", action="store_true", help="print in uppercase")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if args.times < 1:
        raise ValueError("--times must be at least 1")
    message = f"{args.greeting}, {', '.join(args.name)}!"
    if args.shout:
        message = message.upper()
    for _ in range(args.times):
        print(message)
    return 0
