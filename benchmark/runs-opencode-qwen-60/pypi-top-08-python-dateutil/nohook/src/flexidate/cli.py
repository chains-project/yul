"""Command-line interface for flexidate."""

import argparse
import sys
from datetime import datetime

from flexidate.parser import parse_date, parse_date_range, parse_multiple_dates
from flexidate.relative import relative_date, RelativeDate


def cmd_parse(args):
    """Handle the 'parse' subcommand."""
    try:
        if args.dates:
            dates = parse_multiple_dates(args.dates)
            for d in dates:
                print(d.isoformat())
        elif args.start and args.end:
            start, end = parse_date_range(args.start, args.end)
            print(f"{start.isoformat()} to {end.isoformat()}")
        else:
            date_str = args.date
            if date_str:
                result = parse_date(date_str)
                print(result.isoformat())
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_relative(args):
    """Handle the 'relative' subcommand."""
    base = None
    if args.base:
        try:
            base = parse_date(args.base)
        except ValueError as e:
            print(f"Error parsing base date: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        result = relative_date(args.expression, base)
        print(result.isoformat())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_diff(args):
    """Handle the 'diff' subcommand."""
    base = datetime.now()
    if args.base:
        try:
            base = parse_date(args.base)
        except ValueError as e:
            print(f"Error parsing base date: {e}", file=sys.stderr)
            sys.exit(1)

    target = parse_date(args.date)
    rd = RelativeDate(base)
    diff_value = rd.diff(target, args.unit)

    if args.unit in ("years", "months"):
        print(f"{diff_value:.2f} {args.unit}")
    else:
        print(f"{diff_value:.0f} {args.unit}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="flexidate",
        description="Parse dates and compute relative date arithmetic",
    )
    subparsers = parser.add_subparsers(dest="command")

    parse_parser = subparsers.add_parser("parse", help="Parse date string(s)")
    parse_parser.add_argument("date", nargs="?", help="Date string to parse")
    parse_parser.add_argument("dates", nargs="+", help="Multiple date strings")
    parse_parser.add_argument("--start", help="Start date")
    parse_parser.add_argument("--end", help="End date")

    relative_parser = subparsers.add_parser(
        "relative", help="Compute relative date from expression"
    )
    relative_parser.add_argument("expression", help="Relative date expression")
    relative_parser.add_argument(
        "--base", help="Base datetime (defaults to now)"
    )

    diff_parser = subparsers.add_parser("diff", help="Calculate date difference")
    diff_parser.add_argument("date", help="Target date")
    diff_parser.add_argument(
        "--base", help="Base datetime (defaults to now)"
    )
    diff_parser.add_argument(
        "--unit",
        default="days",
        choices=["years", "months", "weeks", "days", "hours", "minutes", "seconds"],
        help="Unit for the difference",
    )

    args = parser.parse_args()

    if args.command == "parse":
        cmd_parse(args)
    elif args.command == "relative":
        cmd_relative(args)
    elif args.command == "diff":
        cmd_diff(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()