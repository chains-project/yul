"""The ``calc`` subcommand."""

from __future__ import annotations

import argparse
from functools import reduce

NAME = "calc"
HELP = "Evaluate simple arithmetic over one or more numbers."

_OPERATIONS = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "div": lambda a, b: a / b,
}


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "operation",
        choices=sorted(_OPERATIONS),
        help="operation to apply, left to right",
    )
    parser.add_argument(
        "operands",
        nargs="+",
        type=float,
        metavar="N",
        help="numbers to operate on",
    )
    parser.add_argument(
        "-p",
        "--precision",
        type=int,
        default=6,
        metavar="D",
        help="decimal places in the result (default: %(default)s)",
    )


def run(args: argparse.Namespace) -> int:
    op = _OPERATIONS[args.operation]
    try:
        result = reduce(op, args.operands)
    except ZeroDivisionError:
        print("error: division by zero")
        return 1
    print(f"{result:.{args.precision}f}")
    return 0
