"""Command-line entry point: ``datewise "the first Monday of next month"``."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from datewise.parse import DateParseError, parse_date


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse human-written date expressions."
    )
    parser.add_argument("expression", nargs="+", help="e.g. 'next Friday'")
    parser.add_argument(
        "--today",
        type=date.fromisoformat,
        help="Reference date (YYYY-MM-DD) for relative expressions",
    )
    args = parser.parse_args(argv)

    try:
        result = parse_date(" ".join(args.expression), today=args.today)
    except DateParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{result.isoformat()}  ({result:%A})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
