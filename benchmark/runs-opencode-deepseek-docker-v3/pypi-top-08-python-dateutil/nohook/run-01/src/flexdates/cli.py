"""Command line entry point for flexdates."""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from .parser import parse_date


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flexdates",
        description="Parse a human-written date string and print it as ISO 8601.",
    )
    parser.add_argument("text", help="the date phrase, e.g. 'first monday of next month'")
    parser.add_argument(
        "--base",
        help="anchor for relative phrases (ISO 8601, e.g. 2026-01-01T09:00:00)",
    )
    parser.add_argument(
        "--past",
        action="store_true",
        help="prefer past dates when a phrase is ambiguous",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    base: dt.datetime | None = None
    if args.base:
        try:
            base = dt.datetime.fromisoformat(args.base)
        except ValueError:
            print(f"error: invalid --base value: {args.base!r}", file=sys.stderr)
            return 2

    try:
        result = parse_date(
            args.text,
            base=base,
            prefer_dates_from="past" if args.past else "future",
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if result is None:
        print(f"error: could not parse {args.text!r}", file=sys.stderr)
        return 1

    print(result.isoformat())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
