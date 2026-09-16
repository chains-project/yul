#!/usr/bin/env python3
"""Entry point for worldtime CLI."""

import argparse
import json
from datetime import datetime

from worldtime import now_in_tz, convert_time, format_comparison, list_timezones
import pytz


def main():
    parser = argparse.ArgumentParser(
        description="Work with timezone-aware datetimes across regions"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # now command
    now_parser = subparsers.add_parser("now", help="Show current time in a timezone")
    now_parser.add_argument(
        "timezone",
        nargs="?",
        default="utc",
        help="Timezone alias (default: utc)",
    )

    # compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare time across multiple timezones"
    )
    compare_parser.add_argument(
        "timezones",
        nargs="+",
        help="Timezone aliases to compare",
    )

    # convert command
    convert_parser = subparsers.add_parser(
        "convert", help="Convert a datetime between timezones"
    )
    convert_parser.add_argument(
        "datetime_str", help="Datetime to convert (YYYY-MM-DD HH:MM:SS)"
    )
    convert_parser.add_argument("from_tz", help="Source timezone alias")
    convert_parser.add_argument("to_tz", help="Target timezone alias")

    # list command
    list_parser = subparsers.add_parser(
        "list", help="List available timezone aliases"
    )

    args = parser.parse_args()

    if args.command == "now":
        dt = now_in_tz(args.timezone)
        print(dt.strftime("%Y-%m-%d %H:%M:%S %Z%z"))

    elif args.command == "compare":
        results = format_comparison(datetime.now(pytz.UTC), args.timezones)
        for tz_name, formatted in results.items():
            print(f"{tz_name:20s} {formatted}")

    elif args.command == "convert":
        dt = datetime.strptime(args.datetime_str, "%Y-%m-%d %H:%M:%S")
        converted = convert_time(dt, args.from_tz, args.to_tz)
        print(
            f"{args.datetime_str} {args.from_tz} -> "
            f"{converted.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
        )

    elif args.command == "list":
        tzs = list_timezones()
        for alias, tz_name in sorted(tzs.items()):
            print(f"{alias:20s} {tz_name}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()