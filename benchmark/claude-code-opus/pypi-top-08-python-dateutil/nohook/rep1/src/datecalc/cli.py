import argparse
import sys
from datetime import date

from datecalc.parse import DateParseError, resolve


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Resolve human-written date expressions to ISO dates."
    )
    parser.add_argument("expression", nargs="+", help='e.g. "first Monday of next month"')
    parser.add_argument(
        "--base",
        type=date.fromisoformat,
        default=None,
        help="Reference date (YYYY-MM-DD); defaults to today",
    )
    args = parser.parse_args(argv)

    try:
        result = resolve(" ".join(args.expression), base=args.base)
    except DateParseError as e:
        sys.exit(f"error: {e}")
    print(result.isoformat())
