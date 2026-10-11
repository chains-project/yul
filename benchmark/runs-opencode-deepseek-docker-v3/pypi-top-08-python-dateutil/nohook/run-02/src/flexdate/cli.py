"""Command line entry point: ``flexdate "<date string>"``."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .core import resolve


def build_parser():
    parser = argparse.ArgumentParser(
        prog="flexdate",
        description="Parse a human-written date string and print the resolved date.",
    )
    parser.add_argument("date", help="e.g. 'the first Monday of next month'")
    parser.add_argument(
        "--base",
        metavar="DATE",
        help="reference date used for relative phrases (default: now)",
    )
    parser.add_argument(
        "--format",
        default="%Y-%m-%d",
        help="strftime output format (default: %%Y-%%m-%%d)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    base = datetime.fromisoformat(args.base) if args.base else None
    try:
        result = resolve(args.date, base=base)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(result.strftime(args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
