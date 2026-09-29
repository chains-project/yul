"""Command-line interface for dateflex."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .parser import parse_when


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dateflex",
        description="Parse flexible, human-written date expressions.",
    )
    parser.add_argument("expression", help="e.g. 'first Monday of next month'")
    parser.add_argument(
        "--base",
        help="reference date/time in ISO format (defaults to now)",
    )
    parser.add_argument(
        "--date-only",
        action="store_true",
        help="print only the date portion (YYYY-MM-DD)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    base = datetime.fromisoformat(args.base) if args.base else None

    try:
        result = parse_when(args.expression, base)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.date().isoformat() if args.date_only else result.isoformat())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
