"""Command line entry point: ``flexdate "the first Monday of next month"``."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .errors import DateParseError
from .parser import parse


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="flexdate",
        description="Parse a human-written date string and print it in ISO format.",
    )
    parser.add_argument("text", nargs="+", help="the date phrase to parse")
    parser.add_argument(
        "-f",
        "--format",
        default="%Y-%m-%d",
        help="strftime output format (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    try:
        result = parse(" ".join(args.text))
    except DateParseError as exc:
        print(f"flexdate: error: {exc}", file=sys.stderr)
        return 1

    print(result.strftime(args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
