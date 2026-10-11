"""Relative date arithmetic helpers."""

from __future__ import annotations

import calendar
import datetime as dt

from dateutil.relativedelta import relativedelta

__all__ = [
    "DateDelta",
    "WEEKDAYS",
    "add_to_date",
    "nth_weekday_of_month",
]

DateDelta = relativedelta

WEEKDAYS: dict[str, int] = {
    name.lower(): index for index, name in enumerate(calendar.day_name)
}
WEEKDAYS.update(
    {
        "mon": 0,
        "tue": 1,
        "tues": 1,
        "wed": 2,
        "thu": 3,
        "thur": 3,
        "thurs": 3,
        "fri": 4,
        "sat": 5,
        "sun": 6,
    }
)


def weekday_index(value: int | str) -> int:
    """Return the Monday-based index (0-6) for a weekday name or int."""
    if isinstance(value, int):
        if not 0 <= value <= 6:
            raise ValueError("weekday index must be between 0 and 6")
        return value
    try:
        return WEEKDAYS[value.strip().lower()]
    except KeyError:
        raise ValueError(f"unknown weekday: {value!r}") from None


def nth_weekday_of_month(
    year: int,
    month: int,
    weekday: int | str,
    n: int = 1,
) -> dt.date:
    """Return the ``n``-th weekday of a month.

    ``n`` is 1-based ("first" is 1) and ``n=-1`` means "last". Raises
    ``ValueError`` when the requested occurrence does not exist.
    """
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    if n == 0:
        raise ValueError("n must be non-zero; use -1 for the last occurrence")

    weekday = weekday_index(weekday)
    days_in_month = calendar.monthrange(year, month)[1]

    if n < 0:
        last = dt.date(year, month, days_in_month)
        offset = (last.weekday() - weekday) % 7
        return last - dt.timedelta(days=offset)

    first = dt.date(year, month, 1)
    day = 1 + (weekday - first.weekday()) % 7 + (n - 1) * 7
    if day > days_in_month:
        raise ValueError(
            f"{year}-{month:02d} has no occurrence {n} of weekday {weekday}"
        )
    return dt.date(year, month, day)


def add_to_date(
    base: dt.date | dt.datetime,
    /,
    *,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> dt.date | dt.datetime:
    """Add a relative delta to ``base``, preserving the input type."""
    return base + relativedelta(
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )
