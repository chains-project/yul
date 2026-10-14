"""Parse human-written date strings and do calendar-aware date arithmetic."""

from __future__ import annotations

import datetime as dt
import re

import dateparser
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU, relativedelta

WEEKDAYS = {
    "monday": MO, "tuesday": TU, "wednesday": WE, "thursday": TH,
    "friday": FR, "saturday": SA, "sunday": SU,
}
ORDINALS = {
    "first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4, "fifth": 5, "5th": 5, "last": -1,
}
MONTH_OFFSETS = {"this": 0, "next": 1, "last": -1, "previous": -1}

_WD = "|".join(WEEKDAYS)
# "the first monday of next month", "last friday of this month"
_NTH_OF_MONTH = re.compile(
    rf"^(?:the\s+)?(?P<ord>{'|'.join(ORDINALS)})\s+(?P<wd>{_WD})\s+of\s+"
    rf"(?:the\s+)?(?P<rel>{'|'.join(MONTH_OFFSETS)})\s+month$"
)
# "next friday", "last tuesday", "this sunday"
_REL_WEEKDAY = re.compile(rf"^(?P<rel>next|last|this)\s+(?P<wd>{_WD})$")


def _parse_rules(text: str, base: dt.date) -> dt.date | None:
    """Handle phrases dateparser doesn't understand. Returns None if no rule matches."""
    text = " ".join(text.lower().split())
    if m := _NTH_OF_MONTH.match(text):
        return nth_weekday_of_relative_month(
            m["wd"], ORDINALS[m["ord"]], months=MONTH_OFFSETS[m["rel"]], base=base
        )
    if m := _REL_WEEKDAY.match(text):
        wd = WEEKDAYS[m["wd"]]
        if m["rel"] == "next":  # strictly after today
            return base + relativedelta(days=1, weekday=wd(+1))
        if m["rel"] == "last":  # strictly before today
            return base + relativedelta(days=-1, weekday=wd(-1))
        return base + relativedelta(weekday=wd(+1))  # "this": today or later
    return None


def parse(text: str, *, base: dt.date | None = None) -> dt.date:
    """Parse a free-form date string ("next friday", "in 3 weeks", "12 Jan 2027",
    "the first monday of next month").

    Relative expressions are resolved against ``base`` (default: today).
    Raises ValueError if the string can't be understood.
    """
    base = base or dt.date.today()
    if (ruled := _parse_rules(text, base)) is not None:
        return ruled
    settings = {
        "RELATIVE_BASE": dt.datetime.combine(base, dt.time()),
        "PREFER_DATES_FROM": "future",
    }
    result = dateparser.parse(text, settings=settings)
    if result is None:
        raise ValueError(f"Could not parse date: {text!r}")
    return result.date()


def nth_weekday_of_month(year: int, month: int, weekday: str, n: int) -> dt.date:
    """The nth weekday of a month. n=1 is first, n=-1 is last.

    >>> nth_weekday_of_month(2026, 11, "thursday", 4)  # US Thanksgiving
    datetime.date(2026, 11, 26)
    """
    if n == 0:
        raise ValueError("n must be non-zero")
    wd = WEEKDAYS[weekday.lower()]
    first = dt.date(year, month, 1)
    if n > 0:
        result = first + relativedelta(weekday=wd(n))
    else:
        result = first + relativedelta(day=31, weekday=wd(n))
    if result.month != month:
        raise ValueError(f"There is no {n}th {weekday} in {year}-{month:02d}")
    return result


def nth_weekday_of_relative_month(
    weekday: str, n: int = 1, *, months: int = 1, base: dt.date | None = None
) -> dt.date:
    """nth weekday of the month ``months`` away from ``base``.

    "the first Monday of next month" -> nth_weekday_of_relative_month("monday", 1)
    "the last Friday of this month"  -> nth_weekday_of_relative_month("friday", -1, months=0)
    """
    target = (base or dt.date.today()) + relativedelta(months=months, day=1)
    return nth_weekday_of_month(target.year, target.month, weekday, n)


def shift(base: dt.date, **delta: int) -> dt.date:
    """Calendar-aware shift: shift(d, months=1) on Jan 31 gives Feb 28/29, not Mar 3."""
    return base + relativedelta(**delta)
