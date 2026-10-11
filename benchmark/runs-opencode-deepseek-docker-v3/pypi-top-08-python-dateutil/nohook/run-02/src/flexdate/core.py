"""Flexible date parsing and relative date arithmetic.

The module exposes a small, predictable API:

* :func:`parse_date` turns a human-written string (``"tomorrow 5pm"``,
  ``"March 3 2026"``, ``"in 2 weeks"``) into a ``datetime``.
* :func:`resolve` additionally understands calendar-relative phrases such as
  ``"the first Monday of next month"`` and ``"the last Friday of this month"``.
* :func:`nth_weekday_of_month` is the low-level building block.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

__all__ = [
    "WEEKDAYS",
    "ORDINALS",
    "parse_date",
    "resolve",
    "nth_weekday_of_month",
    "first_weekday_of_month",
    "last_weekday_of_month",
]

WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
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

_NTH_WEEKDAY_RE = re.compile(
    r"^\s*(?:the\s+)?(?P<ord>[a-z0-9]+)\s+(?P<weekday>[a-z]+)\s+of\s+(?P<month>.+?)\s*$",
    re.IGNORECASE,
)

_DEFAULT_SETTINGS = {
    "RETURN_AS_TIMEZONE_AWARE": False,
    "PREFER_DATES_FROM": "future",
}


def _as_base(base):
    """Normalise ``base`` into a ``datetime`` used as the relative reference."""
    if base is None:
        return datetime.now()
    if isinstance(base, datetime):
        return base
    if isinstance(base, date):
        return datetime(base.year, base.month, base.day)
    if isinstance(base, str):
        return parse_date(base)
    raise TypeError(f"base must be a date, datetime, str or None, got {type(base)!r}")


def _weekday_index(weekday):
    if isinstance(weekday, int):
        if 0 <= weekday <= 6:
            return weekday
        raise ValueError(f"weekday index must be between 0 and 6, got {weekday}")
    key = weekday.strip().lower()
    if key not in WEEKDAYS:
        raise ValueError(f"unknown weekday: {weekday!r}")
    return WEEKDAYS[key]


def _parse_date(text, base, settings=None):
    merged = dict(_DEFAULT_SETTINGS)
    merged["RELATIVE_BASE"] = base
    if settings:
        merged.update(settings)
    try:
        import dateparser
    except ImportError:
        dateparser = None

    parsed = None
    if dateparser is not None:
        parsed = dateparser.parse(text, settings=merged)
    if parsed is None:
        parsed = dateutil_parser.parse(text, default=base)
    return parsed


def parse_date(text, base=None, settings=None):
    """Parse a flexible, human-written date string into a ``datetime``.

    >>> parse_date("2026-03-03").date().isoformat()
    '2026-03-03'
    """
    return _parse_date(text, _as_base(base), settings)


def nth_weekday_of_month(n, weekday, year=None, month=None, base=None):
    """Return the ``n``-th ``weekday`` of a month.

    ``n`` may be negative (``-1`` is the last occurrence) or use a name such as
    ``"first"`` / ``"last"``. When ``year``/``month`` are omitted they are taken
    from ``base`` (defaults to now).
    """
    if isinstance(n, str):
        key = n.strip().lower()
        if key not in ORDINALS:
            raise ValueError(f"unknown ordinal: {n!r}")
        n = ORDINALS[key]
    if n == 0:
        raise ValueError("n must not be zero")

    if year is None or month is None:
        ref = _as_base(base)
        year = ref.year if year is None else year
        month = ref.month if month is None else month

    weekday_index = _weekday_index(weekday)
    weeks = calendar.monthcalendar(year, month)
    days = [week[weekday_index] for week in weeks if week[weekday_index] != 0]
    try:
        day = days[n - 1] if n > 0 else days[n]
    except IndexError:
        label = "last" if n < 0 else f"{n}th"
        raise ValueError(f"{year}-{month:02d} has no {label} matching weekday") from None
    return datetime(year, month, day)


def first_weekday_of_month(weekday, year=None, month=None, base=None):
    """Return the first ``weekday`` of a month."""
    return nth_weekday_of_month(1, weekday, year=year, month=month, base=base)


def last_weekday_of_month(weekday, year=None, month=None, base=None):
    """Return the last ``weekday`` of a month."""
    return nth_weekday_of_month(-1, weekday, year=year, month=month, base=base)


def _resolve_month_ref(ref, base):
    text = ref.strip().lower()
    if text in ("this month", "current month"):
        return base.year, base.month
    if text == "next month":
        shifted = base + relativedelta(months=1)
        return shifted.year, shifted.month
    if text in ("last month", "previous month"):
        shifted = base + relativedelta(months=-1)
        return shifted.year, shifted.month
    if text.startswith("in "):
        text = text[3:].strip()
    parsed = _parse_date(text, base)
    return parsed.year, parsed.month


def resolve(text, base=None, settings=None):
    """Parse a date string, including calendar-relative phrases.

    Supports natural language (via ``dateparser``/``dateutil``) as well as
    patterns such as ``"the first Monday of next month"`` and
    ``"last Friday of March 2026"``.

    >>> from datetime import datetime
    >>> resolve("the first Monday of next month", base=datetime(2026, 3, 15))
    datetime.datetime(2026, 4, 6, 0, 0)
    """
    ref = _as_base(base)
    match = _NTH_WEEKDAY_RE.match(text)
    if match:
        ordinal = match.group("ord").lower()
        weekday = match.group("weekday").lower()
        if ordinal in ORDINALS and weekday in WEEKDAYS:
            year, month = _resolve_month_ref(match.group("month"), ref)
            return nth_weekday_of_month(ORDINALS[ordinal], WEEKDAYS[weekday], year, month)

    parsed = _parse_date(text, ref, settings)
    if parsed is None:
        raise ValueError(f"could not parse date: {text!r}")
    return parsed
