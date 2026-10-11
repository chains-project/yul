"""Parse flexible, human-written date strings."""

from __future__ import annotations

import calendar
import datetime as dt
import re

from dateparser import parse as _dateparser_parse

from .relative import add_to_date, nth_weekday_of_month

__all__ = ["parse_date"]

_ORDINAL_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "last": -1,
}

_WEEKDAY_NAMES = "|".join(
    name.lower()
    for name in (*calendar.day_name, "mon", "tue", "tues", "wed", "thu", "thur", "thurs", "fri", "sat", "sun")
)

_MONTH_NAMES = {
    name.lower(): index for index, name in enumerate(calendar.month_name) if name
}
_MONTH_NAMES.update(
    {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "sept": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
)

_ORDINAL_PATTERN = re.compile(
    rf"^(?:the\s+)?"
    rf"(?P<ordinal>first|second|third|fourth|fifth|last|\d+(?:st|nd|rd|th))"
    rf"\s+(?P<weekday>{_WEEKDAY_NAMES})"
    rf"\s+(?:of|in)\s+(?P<month>.+)$",
    re.IGNORECASE,
)

_MONTH_OFFSET_PATTERN = re.compile(
    r"^(?P<direction>next|coming|this|current|last|previous)\s+month$",
    re.IGNORECASE,
)
_IN_MONTHS_PATTERN = re.compile(
    r"^(?:in\s+)?(?P<count>\d+)\s+months?$", re.IGNORECASE
)
_MONTH_YEAR_PATTERN = re.compile(
    r"^(?P<name>[a-z]+)(?:\s+(?P<year>\d{4}))?$", re.IGNORECASE
)


def _normalize_base(base: dt.date | dt.datetime | None) -> dt.datetime:
    if base is None:
        return dt.datetime.now()
    if isinstance(base, dt.datetime):
        return base
    if isinstance(base, dt.date):
        return dt.datetime.combine(base, dt.time.min)
    raise TypeError(f"base must be a date, datetime or None, got {type(base).__name__}")


def _combine(day: dt.date, base: dt.datetime) -> dt.datetime:
    return dt.datetime(
        day.year,
        day.month,
        day.day,
        base.hour,
        base.minute,
        base.second,
        base.microsecond,
        tzinfo=base.tzinfo,
    )


def _parse_ordinal(token: str) -> int:
    token = token.lower()
    if token in _ORDINAL_WORDS:
        return _ORDINAL_WORDS[token]
    return int(re.sub(r"(st|nd|rd|th)$", "", token))


def _resolve_month(ref: str, base: dt.datetime) -> tuple[int, int]:
    ref = ref.strip().lower()

    offset = _MONTH_OFFSET_PATTERN.match(ref)
    if offset:
        direction = offset.group("direction")
        if direction in ("next", "coming"):
            shifted = add_to_date(base, months=1)
        elif direction in ("last", "previous"):
            shifted = add_to_date(base, months=-1)
        else:
            shifted = base
        return shifted.year, shifted.month

    in_months = _IN_MONTHS_PATTERN.match(ref)
    if in_months:
        shifted = add_to_date(base, months=int(in_months.group("count")))
        return shifted.year, shifted.month

    named = _MONTH_YEAR_PATTERN.match(ref)
    if named and named.group("name") in _MONTH_NAMES:
        month = _MONTH_NAMES[named.group("name")]
        year = int(named.group("year")) if named.group("year") else base.year
        return year, month

    raise ValueError(f"could not resolve month reference: {ref!r}")


def parse_date(
    text: str,
    *,
    base: dt.date | dt.datetime | None = None,
    prefer_dates_from: str = "future",
) -> dt.datetime | None:
    """Parse a human-written date string into a ``datetime``.

    Handles natural phrases supported by ``dateparser`` ("tomorrow", "in 2
    weeks", "Jan 5 2027", ...) plus ordinal weekday phrases such as
    "the first Monday of next month" and "last Friday of March 2027".

    ``base`` anchors relative phrases; it defaults to the current time.
    Returns ``None`` when the string cannot be interpreted.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text.strip():
        return None

    base_dt = _normalize_base(base)
    ordinal = _ORDINAL_PATTERN.match(text.strip())
    if ordinal:
        year, month = _resolve_month(ordinal.group("month"), base_dt)
        n = _parse_ordinal(ordinal.group("ordinal"))
        day = nth_weekday_of_month(year, month, ordinal.group("weekday"), n)
        return _combine(day, base_dt)

    return _dateparser_parse(
        text,
        settings={
            "RELATIVE_BASE": base_dt,
            "PREFER_DATES_FROM": prefer_dates_from,
            "RETURN_AS_TIMEZONE_AWARE": base_dt.tzinfo is not None,
        },
    )
