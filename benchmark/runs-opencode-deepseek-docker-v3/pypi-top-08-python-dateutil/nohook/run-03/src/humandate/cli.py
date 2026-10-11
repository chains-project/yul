"""Command-line interface for humandate."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional, Sequence

from .parser import parse


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="humandate",
        description="Parse a human-written date expression and print the result.",
    )
    parser.add_argument("expression", help='e.g. "the first Monday of next month"')
    parser.add_argument(
        "--base",
        help="Base date/time (ISO 8601) used for relative expressions. Defaults to now.",
    )
    parser.add_argument(
        "--iso",
        action="store_true",
        help="Print the result in ISO 8601 format.",
    )
    args = parser.parse_args(argv)

    base = None
    if args.base:
        try:
            base = datetime.fromisoformat(args.base)
        except ValueError:
            print(f"error: invalid --base value: {args.base!r}", file=sys.stderr)
            return 2

    try:
        result = parse(args.expression, base=base)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.isoformat() if args.iso else result.strftime("%Y-%m-%d %H:%M:%S"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
