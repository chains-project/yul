"""The ``greet`` subcommand: a simple command with positional and optional args."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "greet",
        help="Print a greeting.",
        description="Print a customizable greeting to a name.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="Who to greet (default: world).",
    )
    parser.add_argument(
        "-g",
        "--greeting",
        default="Hello",
        help="Greeting word (default: Hello).",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="Number of times to greet (default: 1).",
    )
    parser.add_argument(
        "-u",
        "--uppercase",
        action="store_true",
        help="Uppercase the output.",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    message = f"{args.greeting}, {args.name}!"
    if args.uppercase:
        message = message.upper()
    for _ in range(max(args.count, 0)):
        print(message)
    return 0
