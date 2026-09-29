"""Core parsing and arithmetic helpers.

Two complementary capabilities live here:

* :func:`parse` turns a flexible, human-written string into a ``datetime``.
  It understands the phrases ``python-dateutil`` already handles (``"2026-09-27"``,
  ``"Sept 27 2026"``, ``"next friday"`` ...) plus ordinal-weekday phrases such
  as ``"the first Monday of next month"`` and ``"last Friday of March 2027"``.
* :func:`shift` performs relative calendar arithmetic (months, years, weekdays)
  on any parsed value.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from dateutil import parser as _dateutil_parser
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

DateLike = str | date | datetime

_WEEKDAYS = {
    "monday": MO, "mon": MO,
    "tuesday": TU, "tue": TU, "tues": TU,
    "wednesday": WE, "wed": WE,
    "thursday": TH, "thu": TH, "thur": TH, "thurs": TH,
    "friday": FR, "fri": FR,
    "saturday": SA, "sat": SA,
    "sunday": SU, "sun": SU,
}

_ORDINALS = {
    "first": 1, "1st": 1,
    "second": 2, "2nd": 2,
    "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4,
    "fifth": 5, "5th": 5,
    "last": -1,
}

_NTH_WEEKDAY_RE = re.compile(
    r"^\s*(?:the\s+)?(?P<ordinal>first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|last)"
    r"\s+(?P<weekday>[a-z]+)"
    r"\s+of\s+(?P<period>.+?)\s*$",
    re.IGNORECASE,
)


def _resolve_period(text: str, today: datetime) -> datetime:
    """Resolve the period part of an ordinal-weekday phrase to its first day."""
    period = " ".join(text.lower().split())

    if period in {"this month", "current month"}:
        return today.replace(day=1)
    if period in {"next month"}:
        return (today + relativedelta(months=1)).replace(day=1)
    if period in {"last month", "previous month"}:
        return (today + relativedelta(months=-1)).replace(day=1)

    if period in {"this year", "current year"}:
        return today.replace(month=1, day=1)
    if period == "next year":
        return (today + relativedelta(years=1)).replace(month=1, day=1)
    if period in {"last year", "previous year"}:
        return (today + relativedelta(years=-1)).replace(month=1, day=1)

    parsed = _dateutil_parser.parse(period, default=today.replace(day=1))
    return parsed.replace(day=1)


def _parse_nth_weekday(text: str, today: datetime) -> datetime | None:
    match = _NTH_WEEKDAY_RE.match(text)
    if not match:
        return None

    weekday = _WEEKDAYS.get(match.group("weekday").lower())
    if weekday is None:
        return None

    ordinal = _ORDINALS[match.group("ordinal").lower()]
    base = _resolve_period(match.group("period"), today)

    if ordinal == -1:
        anchor = base + relativedelta(months=1, days=-1)
    else:
        anchor = base

    return anchor + relativedelta(weekday=weekday(ordinal))


def parse(
    value: DateLike,
    *,
    default: datetime | None = None,
    dayfirst: bool = False,
    yearfirst: bool = False,
) -> datetime:
    """Parse ``value`` into a :class:`datetime.datetime`.

    ``default`` supplies the values used to fill in any missing components
    (and is also the reference point for phrases like ``"next month"``); it
    defaults to now.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)

    text = str(value).strip()
    if not text:
        raise ValueError("cannot parse an empty date string")

    today = default or datetime.now()

    nth = _parse_nth_weekday(text, today)
    if nth is not None:
        return nth

    return _dateutil_parser.parse(
        text,
        default=default,
        dayfirst=dayfirst,
        yearfirst=yearfirst,
    )


def shift(value: DateLike, **kwargs: int) -> datetime:
    """Add a :class:`relativedelta` amount to ``value``.

    Named arguments use ``relativedelta`` semantics, e.g.
    ``shift("2026-09-27", months=1, weekday=MO(1))`` -> first Monday of
    October 2026.
    """
    base = parse(value) if not isinstance(value, datetime) else value
    return base + relativedelta(**kwargs)
