"""Parse human-written date strings and compute relative date arithmetic."""

from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import MO, relativedelta


def parse_date(text: str) -> datetime:
    """Parse a flexible, human-written date string into a datetime."""
    return parser.parse(text, fuzzy=True)


def first_weekday_of_next_month(reference: datetime, weekday=MO) -> datetime:
    """Return the first occurrence of `weekday` in the month after `reference`."""
    next_month = reference + relativedelta(months=1, day=1)
    return next_month + relativedelta(weekday=weekday(1))


if __name__ == "__main__":
    now = datetime.now()
    print(f"Reference date: {now.date()}")
    print(f"First Monday of next month: {first_weekday_of_next_month(now).date()}")

    examples = [
        "next Friday",
        "March 5th, 2026",
        "5th of March 2026",
        "2026-01-15",
        "Jan 3 2026 3pm",
    ]
    for example in examples:
        try:
            print(f"{example!r} -> {parse_date(example)}")
        except (ValueError, OverflowError) as exc:
            print(f"{example!r} -> could not parse ({exc})")
