"""Command-line entry point for dateexpr."""

from __future__ import annotations

import argparse
from datetime import datetime

from .parser import parse_date


def main() -> None:
    argparser = argparse.ArgumentParser(
        prog="dateexpr",
        description="Parse a flexible, human-written date expression and print the resulting date.",
    )
    argparser.add_argument("expression", help="e.g. 'first monday of next month', 'in 3 weeks', 'March 5, 2026'")
    argparser.add_argument(
        "--base",
        help="date to resolve relative expressions against (default: now); accepts anything dateexpr can parse",
    )
    args = argparser.parse_args()

    base = parse_date(args.base) if args.base else datetime.now()
    result = parse_date(args.expression, base=base)
    print(result.strftime("%Y-%m-%d (%A)"))


if __name__ == "__main__":
    main()
