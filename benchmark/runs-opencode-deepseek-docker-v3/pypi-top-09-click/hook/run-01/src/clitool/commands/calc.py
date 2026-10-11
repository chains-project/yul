"""The ``calc`` subcommand: nested subcommands sharing a common implementation."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from functools import reduce

logger = logging.getLogger(__name__)


def _apply(op: Callable[[float, float], float], operands: list[float]) -> float:
    return reduce(op, operands)


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "calc",
        help="Perform arithmetic on numbers.",
        description="Perform arithmetic on one or more numbers.",
    )
    math_subparsers = parser.add_subparsers(
        title="operations",
        dest="operation",
        metavar="OPERATION",
        required=True,
    )

    operations: list[tuple[str, str, Callable[[float, float], float]]] = [
        ("add", "Sum all numbers.", lambda a, b: a + b),
        ("sub", "Subtract numbers from the first.", lambda a, b: a - b),
        ("mul", "Multiply all numbers.", lambda a, b: a * b),
    ]
    for name, help_text, op in operations:
        sub = math_subparsers.add_parser(name, help=help_text, description=help_text)
        sub.add_argument("operands", nargs="+", type=float, metavar="N", help="Numbers to use.")
        sub.set_defaults(handler=_make_handler(name, op))

    div = math_subparsers.add_parser(
        "div",
        help="Divide the first number by the rest.",
        description="Divide the first number by each of the following numbers.",
    )
    div.add_argument("operands", nargs="+", type=float, metavar="N", help="Numbers to use.")
    div.set_defaults(handler=_run_div)


def _make_handler(
    name: str, op: Callable[[float, float], float]
) -> Callable[[argparse.Namespace], int]:
    def handler(args: argparse.Namespace) -> int:
        result = _apply(op, args.operands)
        display: float | int = int(result) if result.is_integer() else result
        print(f"{name}({', '.join(map(str, args.operands))}) = {display}")
        return 0

    return handler


def _run_div(args: argparse.Namespace) -> int:
    operands: list[float] = args.operands
    if any(value == 0 for value in operands[1:]):
        logger.error("division by zero")
        return 1
    result = _apply(lambda a, b: a / b, operands)
    if result.is_integer():
        print(int(result))
    else:
        print(result)
    return 0
