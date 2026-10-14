"""``mytool greet``: positional args, choices, flags, and typed options."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("greet", help="greet one or more people")
    p.add_argument("names", nargs="+", metavar="NAME", help="who to greet")
    p.add_argument(
        "-g", "--greeting", default="Hello",
        help="greeting word (default: %(default)s)",
    )
    p.add_argument(
        "-n", "--times", type=int, default=1, metavar="N",
        help="repeat each greeting N times",
    )
    p.add_argument(
        "--style", choices=("plain", "shout", "whisper"), default="plain",
        help="output style (default: %(default)s)",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    for name in args.names:
        message = f"{args.greeting}, {name}!"
        if args.style == "shout":
            message = message.upper()
        elif args.style == "whisper":
            message = message.lower()
        for _ in range(max(args.times, 0)):
            print(message)
    return 0
