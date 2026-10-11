"""The ``hello`` command: a small demonstration of options and validation."""

from __future__ import annotations

import argparse
import logging

log = logging.getLogger("clitool.hello")


def positive_int(value: str) -> int:
    """``argparse`` type that accepts only integers greater than zero."""
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid integer: {value!r}") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "hello",
        help="print a friendly greeting",
        description="Print a friendly greeting to NAME.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="who to greet (default: %(default)s)",
    )
    parser.add_argument(
        "-g",
        "--greeting",
        default="Hello",
        help="greeting to use (default: %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=positive_int,
        default=1,
        metavar="N",
        help="number of times to greet (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--shout",
        action="store_true",
        help="convert the greeting to upper case",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    message = f"{args.greeting}, {args.name}!"
    if args.shout:
        message = message.upper()
    for _ in range(args.count):
        print(message)
    log.debug("greeted %s %d time(s)", args.name, args.count)
    return 0
