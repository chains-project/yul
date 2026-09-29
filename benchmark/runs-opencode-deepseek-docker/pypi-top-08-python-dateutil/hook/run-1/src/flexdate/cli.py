"""Command line entry point: ``flexdate "<date phrase>"``."""

from __future__ import annotations

import argparse
from datetime import datetime

from flexdate.core import parse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="flexdate",
        description="Parse a flexible, human-written date string.",
    )
    parser.add_argument("text", help="the date phrase to parse")
    parser.add_argument(
        "--now",
        help="reference date used as 'today' (ISO 8601); defaults to now",
    )
    args = parser.parse_args(argv)

    default = datetime.fromisoformat(args.now) if args.now else None
    try:
        result = parse(args.text, default=default)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    print(result.isoformat())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
