"""The ``calc`` subcommand: nested arithmetic operations."""

from __future__ import annotations

import argparse
import functools
import operator
import sys
from typing import Callable, Iterable

Operation = Callable[[Iterable[float]], float]

OPERATIONS: "dict[str, tuple[str, Operation]]" = {
    "add": ("add numbers together", lambda nums: sum(nums)),
    "sub": ("subtract numbers left to right", lambda nums: functools.reduce(operator.sub, nums)),
    "mul": ("multiply numbers together", lambda nums: functools.reduce(operator.mul, nums)),
    "div": ("divide numbers left to right", lambda nums: functools.reduce(operator.truediv, nums)),
}


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "calc",
        help="perform arithmetic",
        description="Perform an arithmetic operation over one or more operands.",
    )
    operations = parser.add_subparsers(
        dest="operation",
        metavar="<op>",
        required=True,
        title="operations",
    )
    for name, (summary, _) in OPERATIONS.items():
        operation = operations.add_parser(name, help=summary)
        operation.add_argument(
            "numbers",
            type=float,
            nargs="+",
            metavar="N",
            help="operands",
        )
        operation.add_argument(
            "-p",
            "--precision",
            type=int,
            default=6,
            metavar="D",
            help="digits after the decimal point (default: 6)",
        )
        operation.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    operation = OPERATIONS[args.operation][1]
    try:
        result = operation(args.numbers)
    except ZeroDivisionError:
        print("error: division by zero", file=sys.stderr)
        return 2
    print(_format(result, args.precision))
    return 0


def _format(value: float, precision: int) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.{precision}f}".rstrip("0").rstrip(".")
