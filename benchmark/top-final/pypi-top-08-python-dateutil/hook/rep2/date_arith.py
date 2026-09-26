"""Parse human-written date strings and compute relative date arithmetic."""

import argparse
import sys
from datetime import date, datetime

from dateutil import parser as date_parser
from dateutil.relativedelta import (
    FR,
    MO,
    SA,
    SU,
    TH,
    TU,
    WE,
    relativedelta,
)

WEEKDAYS = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU,
}


def parse_date(text: str, default: datetime | None = None) -> datetime:
    """Parse a flexible, human-written date string."""
    return date_parser.parse(text, default=default or datetime.now())


def first_weekday_of_next_month(weekday_name: str, from_date: date | None = None) -> date:
    """Return the date of the first given weekday of the month after `from_date`."""
    weekday = WEEKDAYS[weekday_name.lower()]
    today = from_date or date.today()
    next_month_start = today + relativedelta(day=1, months=1)
    return next_month_start + relativedelta(weekday=weekday(+1))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    parse_cmd = sub.add_parser("parse", help="Parse a free-form date string")
    parse_cmd.add_argument("text", help="e.g. 'March 3rd 2025', 'Jan 5 2025', '5/1/2025'")

    weekday_cmd = sub.add_parser(
        "first-weekday-next-month", help="First weekday of next month, e.g. 'monday'"
    )
    weekday_cmd.add_argument("weekday", choices=sorted(WEEKDAYS))

    args = parser.parse_args(argv)

    if args.command == "parse":
        try:
            result = parse_date(args.text)
        except (ValueError, OverflowError) as exc:
            print(f"Could not parse '{args.text}': {exc}", file=sys.stderr)
            return 1
        print(result.isoformat())
    elif args.command == "first-weekday-next-month":
        print(first_weekday_of_next_month(args.weekday).isoformat())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
