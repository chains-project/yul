"""Locate the *n*-th weekday within a calendar month.

These helpers back phrases such as ``"the first Monday of next month"`` and
``"last Friday of March 2027"``, which general-purpose parsers handle poorly.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from .errors import DateParseError

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

WEEKDAYS = {
    "monday": MONDAY,
    "mon": MONDAY,
    "tuesday": TUESDAY,
    "tue": TUESDAY,
    "tues": TUESDAY,
    "wednesday": WEDNESDAY,
    "wed": WEDNESDAY,
    "thursday": THURSDAY,
    "thu": THURSDAY,
    "thur": THURSDAY,
    "thurs": THURSDAY,
    "friday": FRIDAY,
    "fri": FRIDAY,
    "saturday": SATURDAY,
    "sat": SATURDAY,
    "sunday": SUNDAY,
    "sun": SUNDAY,
}

ORDINALS = {
    "first": 1,
    "1st": 1,
    "second": 2,
    "2nd": 2,
    "third": 3,
    "3rd": 3,
    "fourth": 4,
    "4th": 4,
    "fifth": 5,
    "5th": 5,
    "last": -1,
}


def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Return the ``n``-th ``weekday`` of ``month``.

    ``n`` is 1-based; ``n=-1`` selects the last matching weekday. Raises
    :class:`DateParseError` when the requested occurrence does not exist
    (for example a fifth Monday in a month with only four).
    """
    if n == 0:
        raise DateParseError("ordinal 0 is not valid")
    if n < 0:
        last_day = calendar.monthrange(year, month)[1]
        candidate = date(year, month, last_day)
        return candidate - timedelta(days=(candidate.weekday() - weekday) % 7)

    first = date(year, month, 1)
    day = 1 + (weekday - first.weekday()) % 7 + 7 * (n - 1)
    if day > calendar.monthrange(year, month)[1]:
        raise DateParseError(
            f"there is no occurrence {n} of weekday {weekday} in {year}-{month:02d}"
        )
    return date(year, month, day)
