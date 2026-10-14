"""`greet`: positional args, choices, flags, and repeated options."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("greet", help="greet one or more people")
    parser.add_argument("names", nargs="+", metavar="NAME", help="who to greet")
    parser.add_argument(
        "-g", "--greeting", default="Hello", help="greeting to use (default: %(default)s)"
    )
    parser.add_argument(
        "-n", "--times", type=int, default=1, metavar="N", help="repeat each greeting N times"
    )
    parser.add_argument(
        "--style",
        choices=["plain", "shout", "whisper"],
        default="plain",
        help="output style (default: %(default)s)",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    for name in args.names:
        message = f"{args.greeting}, {name}!"
        if args.style == "shout":
            message = message.upper()
        elif args.style == "whisper":
            message = message.lower()
        for _ in range(args.times):
            print(message)
    return 0
