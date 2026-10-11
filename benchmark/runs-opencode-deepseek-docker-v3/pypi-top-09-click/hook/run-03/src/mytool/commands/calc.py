"""The ``calc`` subcommand with nested operation subcommands."""

from __future__ import annotations

import argparse
import functools
import operator
from collections.abc import Callable


def register(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "calc",
        help="Perform arithmetic on numbers.",
        description="Arithmetic with nested subcommands (add, subtract, multiply, divide).",
    )
    ops = parser.add_subparsers(
        title="operations",
        dest="operation",
        metavar="OPERATION",
        required=True,
    )

    definitions: list[tuple[str, Callable[[float, float], float], str]] = [
        ("add", operator.add, "Add the given numbers."),
        ("subtract", operator.sub, "Subtract the given numbers from left to right."),
        ("multiply", operator.mul, "Multiply the given numbers."),
        ("divide", operator.truediv, "Divide the given numbers from left to right."),
    ]
    for name, func, help_text in definitions:
        sub = ops.add_parser(name, help=help_text, description=help_text)
        sub.add_argument(
            "numbers",
            type=float,
            nargs="+",
            metavar="NUM",
            help="one or more numbers",
        )
        sub.set_defaults(func=run, op=func)

    return parser


def run(args: argparse.Namespace) -> int:
    try:
        result = functools.reduce(args.op, args.numbers)
    except ZeroDivisionError:
        print("error: division by zero")
        return 1

    if result.is_integer():
        print(int(result))
    else:
        print(result)
    return 0
