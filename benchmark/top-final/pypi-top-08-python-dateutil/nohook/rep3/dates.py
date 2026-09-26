"""Parse human-written date strings and compute relative date arithmetic."""

from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import MO, relativedelta


def parse_date(text: str) -> datetime:
    """Parse a flexible, human-written date string."""
    return parser.parse(text, fuzzy=True)


def first_weekday_of_next_month(reference: datetime, weekday=MO) -> datetime:
    """Return the first occurrence of `weekday` in the month after `reference`."""
    next_month = reference + relativedelta(months=1, day=1)
    return next_month + relativedelta(weekday=weekday(1))


if __name__ == "__main__":
    now = datetime.now()
    print(f"Now: {now:%Y-%m-%d}")

    example = parse_date("Meeting notes from March 3rd, 2024 at 5pm")
    print(f"Parsed: {example}")

    first_monday = first_weekday_of_next_month(now)
    print(f"First Monday of next month: {first_monday:%Y-%m-%d}")
