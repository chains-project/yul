"""Command-line entry point: ``datephrase "the first Monday of next month"``."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .parser import DatePhraseError, resolve


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="datephrase",
        description="Resolve a human-written date phrase to an ISO-8601 datetime.",
    )
    parser.add_argument("phrase", nargs="+", help="the date phrase to resolve")
    parser.add_argument(
        "--base",
        metavar="DATE",
        help="reference date for relative phrases (defaults to now)",
    )
    parser.add_argument(
        "--past",
        action="store_true",
        help="prefer past dates when a phrase is ambiguous",
    )
    args = parser.parse_args(argv)

    base = resolve(args.base) if args.base else None

    try:
        result = resolve(
            " ".join(args.phrase),
            base=base,
            prefer_future=not args.past,
        )
    except (DatePhraseError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.isoformat(sep=" "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
