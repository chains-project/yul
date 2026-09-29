"""Command-line entry point for the ``datephrase`` package."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import List, Optional

from .dates import parse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datephrase",
        description="Parse human-written date phrases relative to a base date.",
    )
    parser.add_argument(
        "phrases",
        nargs="*",
        help="date phrases to resolve; when omitted they are read from stdin",
    )
    parser.add_argument(
        "-b",
        "--base",
        help="reference date/time as ISO 8601 (defaults to now)",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="%Y-%m-%d",
        help="strftime output format (default: %%(Y-%%m-%%d))",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    base: Optional[datetime] = None
    if args.base:
        try:
            base = datetime.fromisoformat(args.base)
        except ValueError:
            print(f"error: invalid --base value: {args.base!r}", file=sys.stderr)
            return 2

    phrases = args.phrases
    if not phrases:
        phrases = [line for line in sys.stdin.read().splitlines() if line.strip()]
    if not phrases:
        print("error: no date phrases given", file=sys.stderr)
        return 2

    exit_code = 0
    for phrase in phrases:
        result = parse(phrase, base=base)
        if result is None:
            print(f"{phrase}: <unable to parse>", file=sys.stderr)
            exit_code = 1
        else:
            print(result.strftime(args.format))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
