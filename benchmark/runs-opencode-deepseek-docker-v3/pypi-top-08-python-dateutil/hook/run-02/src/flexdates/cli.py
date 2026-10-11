"""Command line entry point for flexdates."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from flexdates.core import resolve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="flexdates",
        description="Parse human-written dates like 'the first Monday of next month'.",
    )
    parser.add_argument("text", help="the date expression to resolve")
    parser.add_argument(
        "--base",
        help="reference date/time in ISO format (defaults to now)",
    )
    args = parser.parse_args(argv)

    base = datetime.fromisoformat(args.base) if args.base else None
    result = resolve(args.text, base=base)

    if result is None:
        print(f"could not understand: {args.text!r}", file=sys.stderr)
        return 1

    print(result.isoformat())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
