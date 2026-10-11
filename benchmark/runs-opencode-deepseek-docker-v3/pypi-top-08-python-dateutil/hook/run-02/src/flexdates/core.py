"""Core parsing and date-arithmetic helpers."""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, time, timedelta
from typing import Optional

import dateparser
from dateutil import relativedelta

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

MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})

_WEEKDAY_ALT = "|".join(sorted(WEEKDAYS, key=len, reverse=True))
_ORDINAL_ALT = "|".join(sorted(ORDINALS, key=len, reverse=True))
_MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))

_REL_WEEKDAY_RE = re.compile(
    rf"^\s*(?P<relative>this|next|last)\s+(?P<weekday>{_WEEKDAY_ALT})\s*$",
    re.IGNORECASE,
)

_NTH_WEEKDAY_RE = re.compile(
    rf"""
    ^\s*(?:the\s+)?(?P<ordinal>{_ORDINAL_ALT})\s+
    (?P<weekday>{_WEEKDAY_ALT})\s+of\s+
    (?:
        (?P<relative>this|next|last)\s+month
        |
        (?P<month_name>{_MONTH_ALT})(?:\s+(?P<year>\d{{4}}))?
        |
        (?P<relative_year>this|next|last)\s+year
    )
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


def first_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """Return the first ``weekday`` (0=Monday) of the given month."""
    return nth_weekday(year, month, weekday, 1)


def last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """Return the last ``weekday`` (0=Monday) of the given month."""
    return nth_weekday(year, month, weekday, -1)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Return the ``n``-th ``weekday`` of a month.

    ``n`` is 1-based (1 = first). Pass ``n=-1`` for the last occurrence.
    Raises ``ValueError`` when the requested occurrence does not exist.
    """
    if not 0 <= weekday <= 6:
        raise ValueError("weekday must be between 0 (Monday) and 6 (Sunday)")
    if n == 0:
        raise ValueError("n must be positive, or -1 for the last occurrence")

    days_in_month = calendar.monthrange(year, month)[1]
    if n > 0:
        first = date(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        day = 1 + offset + (n - 1) * 7
        if day > days_in_month:
            raise ValueError(
                f"there is no occurrence {n} of that weekday in "
                f"{calendar.month_name[month]} {year}"
            )
        return date(year, month, day)

    last = date(year, month, days_in_month)
    offset = (last.weekday() - weekday) % 7
    return date(year, month, days_in_month - offset)


def parse(
    text: str,
    base: Optional[datetime] = None,
    settings: Optional[dict] = None,
) -> Optional[datetime]:
    """Parse a flexible, human-written date string.

    Handles everyday expressions such as ``"tomorrow"``, ``"next friday"``,
    ``"in 3 weeks"`` or ``"Jan 5 2027"`` via :mod:`dateparser`. Returns
    ``None`` when the string cannot be understood.
    """
    if base is None:
        base = datetime.now()
    parse_settings = {"RELATIVE_BASE": base}
    if settings:
        parse_settings.update(settings)
    return dateparser.parse(text, languages=["en"], settings=parse_settings)


def resolve(text: str, base: Optional[datetime] = None) -> Optional[datetime]:
    """Resolve a date expression, including ordinal-weekday phrases.

    Extends :func:`parse` with phrases like ``"the first Monday of next
    month"``, ``"last Friday of this month"`` or ``"second Tuesday of
    January 2027"``. Returns ``None`` if nothing can be resolved.
    """
    if base is None:
        base = datetime.now()

    match = _NTH_WEEKDAY_RE.match(text)
    if match:
        return _resolve_nth_weekday(match, base)

    match = _REL_WEEKDAY_RE.match(text)
    if match:
        return _resolve_relative_weekday(match, base)

    return parse(text, base=base)


def _resolve_relative_weekday(match: re.Match, base: datetime) -> datetime:
    relative = match.group("relative").lower()
    weekday = WEEKDAYS[match.group("weekday").lower()]
    midnight = base.replace(hour=0, minute=0, second=0, microsecond=0)

    if relative == "next":
        days = (weekday - base.weekday()) % 7 or 7
    elif relative == "last":
        days = -((base.weekday() - weekday) % 7 or 7)
    else:  # "this": the weekday within the current Monday-based week
        week_start = base - timedelta(days=base.weekday())
        return datetime.combine(week_start.date() + timedelta(days=weekday), time.min)

    return midnight + timedelta(days=days)


def _resolve_nth_weekday(match: re.Match, base: datetime) -> datetime:
    ordinal = ORDINALS[match.group("ordinal").lower()]
    weekday = WEEKDAYS[match.group("weekday").lower()]

    year, month = _resolve_target_month(match, base)
    day = nth_weekday(year, month, weekday, ordinal)
    return datetime.combine(day, time.min)


def _resolve_target_month(match: re.Match, base: datetime) -> tuple[int, int]:
    relative = match.group("relative")
    if relative:
        delta = {"this": 0, "next": 1, "last": -1}[relative.lower()]
        shifted = base + relativedelta.relativedelta(months=delta)
        return shifted.year, shifted.month

    relative_year = match.group("relative_year")
    if relative_year:
        delta = {"this": 0, "next": 1, "last": -1}[relative_year.lower()]
        return base.year + delta, base.month

    month = MONTHS[match.group("month_name").lower()]
    year = match.group("year")
    if year:
        return int(year), month

    resolved_year = base.year
    if month < base.month:
        resolved_year += 1
    return resolved_year, month
