"""Parse flexible, human-written date strings."""

import argparse
from datetime import date

from datewise.parsing import DateParseError, nth_weekday, parse_date

__all__ = ["DateParseError", "nth_weekday", "parse_date", "main"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve a human-written date expression.")
    parser.add_argument("expression", nargs="+", help='e.g. "the first Monday of next month"')
    parser.add_argument("--today", type=date.fromisoformat, help="reference date (YYYY-MM-DD)")
    args = parser.parse_args()

    try:
        result = parse_date(" ".join(args.expression), today=args.today)
    except DateParseError as exc:
        parser.exit(1, f"error: {exc}\n")
    print(f"{result.isoformat()} ({result:%A})")
