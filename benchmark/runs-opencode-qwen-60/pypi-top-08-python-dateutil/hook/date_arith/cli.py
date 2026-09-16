"""Command-line interface for date-arith."""

import argparse

from date_arith.parser import parse_date_string


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Parse flexible date strings and compute relative dates",
    )
    parser.add_argument(
        "date_string",
        help="The date string to parse (e.g., 'the first Monday of next month')",
    )
    parser.add_argument(
        "--reference",
        help="Reference date/time in ISO format (default: now)",
        default=None,
    )

    args = parser.parse_args()

    reference = None
    if args.reference:
        from dateutil import parser as dateutil_parser
        reference = dateutil_parser.parse(args.reference)

    result = parse_date_string(args.date_string, reference)
    print(result.isoformat())


if __name__ == "__main__":
    main()