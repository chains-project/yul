"""Command line entry point: ``datephrase "the first Monday of next month"``."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date, datetime

from datephrase.core import parse


def _base(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.combine(date.fromisoformat(value), datetime.min.time())
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid date: {value!r}") from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="datephrase",
        description="Parse a human-written date phrase.",
    )
    parser.add_argument("text", nargs="+", help="the date phrase to parse")
    parser.add_argument(
        "--base",
        type=_base,
        default=None,
        help="reference date for relative phrases (defaults to now)",
    )
    args = parser.parse_args(argv)

    phrase = " ".join(args.text)
    result = parse(phrase, base=args.base)
    if result is None:
        parser.error(f"could not parse date phrase: {phrase!r}")

    print(result.date().isoformat())
    return 0
