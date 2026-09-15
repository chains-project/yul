"""Parse human-written date strings and compute relative date arithmetic."""

import sys
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

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
    """Parse a loosely formatted date string, e.g. 'next friday', 'March 3 2025'."""
    return parser.parse(text, default=default or datetime.now(), fuzzy=True)


def first_weekday_of_month(weekday_name: str, year: int, month: int) -> datetime:
    """The first occurrence of a given weekday in the specified month."""
    weekday = WEEKDAYS[weekday_name.lower()]
    start = datetime(year, month, 1)
    return start + relativedelta(weekday=weekday(1))


def first_weekday_of_next_month(weekday_name: str, reference: datetime | None = None) -> datetime:
    """e.g. 'the first Monday of next month' relative to a reference date."""
    reference = reference or datetime.now()
    next_month = reference + relativedelta(months=1, day=1)
    return first_weekday_of_month(weekday_name, next_month.year, next_month.month)


def main() -> None:
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print(parse_date(text))
        return

    now = datetime.now()
    print(f"Now: {now}")
    print(f"First Monday of next month: {first_weekday_of_next_month('monday', now)}")
    print(f"Parsed 'next friday at 5pm': {parse_date('next friday at 5pm', now)}")


if __name__ == "__main__":
    main()
