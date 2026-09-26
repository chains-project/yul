"""Parse human-written date strings and compute relative date arithmetic."""

from __future__ import annotations

import sys
from datetime import datetime

from dateutil import parser as date_parser
from dateutil.relativedelta import MO, relativedelta


def parse_date(text: str) -> datetime:
    return date_parser.parse(text, fuzzy=True)


def first_weekday_of_next_month(reference: datetime, weekday=MO) -> datetime:
    next_month = reference + relativedelta(months=1, day=1)
    return next_month + relativedelta(weekday=weekday(+1))


def main(argv: list[str]) -> int:
    text = " ".join(argv[1:]) if len(argv) > 1 else "next Friday"
    reference = parse_date(text)
    print(f"parsed: {reference.isoformat()}")
    print(f"first Monday of next month: {first_weekday_of_next_month(reference).isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
