"""Parse flexible, human-written date strings and compute relative date arithmetic.

Examples::

    >>> parse("next friday", base=date(2026, 9, 27)).date()
    datetime.date(2026, 10, 2)
    >>> parse("the first Monday of next month", base=date(2026, 9, 27)).date()
    datetime.date(2026, 10, 5)
    >>> parse("2 weeks ago", base=date(2026, 9, 27)).date()
    datetime.date(2026, 9, 13)
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Union

from dateparser import parse as _dateparser_parse
from dateutil.relativedelta import relativedelta

__all__ = [
    "WEEKDAYS",
    "nth_weekday_of_month",
    "parse",
    "parse_date",
]

DateLike = Union[date, datetime]

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

_ORDINALS = {
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
    "final": -1,
}

_WEEKDAY_PATTERN = (
    r"mon(?:day)?|tue(?:sday|s)?|wed(?:nesday)?|thu(?:rsday|rs|r)?|"
    r"fri(?:day)?|sat(?:urday)?|sun(?:day)?"
)

_NTH_WEEKDAY_RE = re.compile(
    r"^\s*(?:the\s+)?"
    r"(?P<ord>first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|last|final)"
    r"\s+(?P<weekday>" + _WEEKDAY_PATTERN + r")"
    r"\s+(?:of|in)\s+(?P<period>.+?)\s*$",
    re.IGNORECASE,
)

_BARE_WEEKDAY_RE = re.compile(
    r"^\s*(?:(?P<rel>next|this|last|coming|past|previous)\s+)?"
    r"(?P<weekday>" + _WEEKDAY_PATTERN + r")\s*$",
    re.IGNORECASE,
)

_RELATIVE_MONTHS = {
    "this month": 0,
    "current month": 0,
    "the current month": 0,
    "next month": 1,
    "the next month": 1,
    "last month": -1,
    "previous month": -1,
    "the previous month": -1,
    "month after next": 2,
    "the month after next": 2,
}


def _as_datetime(value: DateLike | None) -> datetime:
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def nth_weekday_of_month(year: int, month: int, n: int, weekday: int) -> date:
    """Return the ``n``-th ``weekday`` (0=Monday) of ``month``.

    ``n`` may be negative to count from the end (``-1`` is the last one).
    Raises ``ValueError`` when the requested occurrence does not exist.
    """
    if not 0 <= weekday <= 6:
        raise ValueError(f"weekday must be in 0..6, got {weekday!r}")
    if n == 0:
        raise ValueError("n must be non-zero")

    first = date(year, month, 1)
    if n > 0:
        offset = (weekday - first.weekday()) % 7
        day = 1 + offset + (n - 1) * 7
        days_in_month = (date(year + (month == 12), month % 12 + 1, 1) - first).days
        if day > days_in_month:
            raise ValueError(f"{year}-{month:02d} has no occurrence number {n} of that weekday")
        return date(year, month, day)

    next_month = date(year + (month == 12), month % 12 + 1, 1)
    last = next_month - timedelta(days=1)
    offset = (last.weekday() - weekday) % 7
    return last - timedelta(days=offset)


def _weekday_from_text(rel: str | None, weekday: int, base: datetime) -> datetime:
    if rel in {"last", "past", "previous"}:
        offset = -((base.weekday() - weekday) % 7) or -7
    elif rel == "next":
        offset = (weekday - base.weekday()) % 7 or 7
    else:  # "this", "coming", or a bare weekday name
        offset = (weekday - base.weekday()) % 7
    return base + timedelta(days=offset)


def _resolve_period(period: str, base: datetime) -> tuple[int, int]:
    key = re.sub(r"^(?:the|of)\s+", "", period.strip().lower())
    if key in _RELATIVE_MONTHS:
        target = base + relativedelta(months=_RELATIVE_MONTHS[key])
    else:
        parsed = _dateparser_parse(period, settings={"RELATIVE_BASE": base})
        if parsed is None:
            raise ValueError(f"could not resolve period {period!r}")
        target = parsed
    return target.year, target.month


def parse(
    text: str,
    base: DateLike | None = None,
    languages: list[str] | None = None,
    **settings,
) -> datetime | None:
    """Parse ``text`` into a ``datetime``, or ``None`` if it cannot be parsed.

    ``base`` is the reference point for relative expressions and defaults to now.
    """
    if not text or not text.strip():
        return None

    reference = _as_datetime(base)

    match = _NTH_WEEKDAY_RE.match(text)
    if match:
        year, month = _resolve_period(match.group("period"), reference)
        n = _ORDINALS[match.group("ord").lower()]
        weekday = WEEKDAYS[match.group("weekday").lower()]
        return datetime.combine(nth_weekday_of_month(year, month, n, weekday), time.min)

    match = _BARE_WEEKDAY_RE.match(text)
    if match:
        weekday = WEEKDAYS[match.group("weekday").lower()]
        return _weekday_from_text(match.group("rel"), weekday, reference)

    settings.setdefault("RELATIVE_BASE", reference)
    if languages is not None:
        settings["languages"] = languages
    return _dateparser_parse(text, settings=settings)


def parse_date(
    text: str,
    base: DateLike | None = None,
    languages: list[str] | None = None,
    **settings,
) -> date | None:
    """Like :func:`parse` but return a ``date`` instead of a ``datetime``."""
    result = parse(text, base=base, languages=languages, **settings)
    return result.date() if result is not None else None
