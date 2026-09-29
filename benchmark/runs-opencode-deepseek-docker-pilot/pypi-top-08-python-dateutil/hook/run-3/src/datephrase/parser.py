"""Parse flexible, human-written date phrases.

The module layers two complementary strategies:

* :mod:`dateparser` handles loose natural-language input such as
  ``"tomorrow at 5pm"``, ``"in 3 days"`` or ``"next friday"``.
* A small resolver on top of :mod:`dateutil.relativedelta` (and the
  :mod:`calendar` module) understands the "Nth <weekday> of <period>"
  family, e.g. ``"the first Monday of next month"``.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, timedelta
from typing import Optional, Tuple, Union

import dateparser
from dateutil.relativedelta import relativedelta

__all__ = ["resolve", "nth_weekday", "DatePhraseError"]

DateLike = Union[date, datetime]


class DatePhraseError(ValueError):
    """Raised when a phrase cannot be understood or has no valid date."""


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

MONTHS = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}
MONTHS.update(
    {name.lower(): index for index, name in enumerate(calendar.month_abbr) if name}
)

_ORDINAL_WEEKDAY_RE = re.compile(
    r"^(?:the\s+)?"
    r"(?P<ordinal>[a-z0-9]+)\s+"
    r"(?P<weekday>[a-z]+)"
    r"(?:\s+(?:of|in)\s+(?P<period>.+))?$",
    re.IGNORECASE,
)


def _as_datetime(value: Optional[DateLike]) -> datetime:
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    raise TypeError(f"base must be a date or datetime, got {type(value).__name__}")


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Return the ``n``-th ``weekday`` of a month (``n == -1`` means last).

    ``weekday`` uses Python's convention: Monday is ``0`` and Sunday is ``6``.
    """
    last_day = calendar.monthrange(year, month)[1]

    if n == -1:
        anchor = date(year, month, last_day)
        return anchor - timedelta(days=(anchor.weekday() - weekday) % 7)

    first = date(year, month, 1)
    day = 1 + (weekday - first.weekday()) % 7 + (n - 1) * 7
    if day > last_day:
        raise DatePhraseError(
            f"there is no {n}th {calendar.day_name[weekday]} in {year}-{month:02d}"
        )
    return date(year, month, day)


def _resolve_month_period(period: str, base: datetime) -> Tuple[int, int]:
    """Turn a period phrase into a ``(year, month)`` pair."""
    text = period.strip().lower()
    text = re.sub(r"^(?:the|of|in)\s+", "", text).strip()

    if text in ("next month", "coming month"):
        shifted = base + relativedelta(months=1)
        return shifted.year, shifted.month
    if text in ("this month", "current month", "the month", ""):
        return base.year, base.month
    if text in ("last month", "previous month", "past month"):
        shifted = base + relativedelta(months=-1)
        return shifted.year, shifted.month

    relative = re.match(r"^(?:in\s+)?(\d+)\s+months?(?:\s+from\s+now)?$", text)
    if relative:
        shifted = base + relativedelta(months=int(relative.group(1)))
        return shifted.year, shifted.month

    named = re.match(r"^([a-z]+)\.?\s*(\d{4})?$", text)
    if named and named.group(1) in MONTHS:
        year = int(named.group(2)) if named.group(2) else base.year
        return year, MONTHS[named.group(1)]

    numeric = re.match(r"^(\d{4})[-/](\d{1,2})(?:[-/]\d{1,2})?$", text)
    if numeric:
        return int(numeric.group(1)), int(numeric.group(2))

    raise DatePhraseError(f"unrecognised month period: {period!r}")


def _resolve_ordinal_weekday(text: str, base: datetime) -> Optional[datetime]:
    match = _ORDINAL_WEEKDAY_RE.match(text)
    if not match:
        return None

    ordinal = ORDINALS.get(match.group("ordinal").lower())
    weekday = WEEKDAYS.get(match.group("weekday").lower())
    if ordinal is None or weekday is None:
        return None

    period = match.group("period") or "this month"
    year, month = _resolve_month_period(period, base)
    resolved = nth_weekday(year, month, weekday, ordinal)
    return datetime.combine(resolved, datetime.min.time())


def resolve(
    text: str,
    *,
    base: Optional[DateLike] = None,
    prefer_future: bool = True,
    languages: Optional[list] = None,
) -> datetime:
    """Resolve a human-written date phrase to a :class:`datetime.datetime`.

    ``base`` anchors relative expressions such as ``"next month"``; it defaults
    to "now". ``prefer_future`` disambiguates phrases that could refer to either
    direction (for example ``"friday"``).
    """
    if not isinstance(text, str):
        raise TypeError(f"phrase must be a string, got {type(text).__name__}")

    phrase = text.strip()
    if not phrase:
        raise DatePhraseError("empty date phrase")

    base_dt = _as_datetime(base)

    ordinal_result = _resolve_ordinal_weekday(phrase, base_dt)
    if ordinal_result is not None:
        return ordinal_result

    parsed = dateparser.parse(
        phrase,
        languages=languages,
        settings={
            "RELATIVE_BASE": base_dt,
            "PREFER_DATES_FROM": "future" if prefer_future else "past",
            "RETURN_AS_TIMEZONE_AWARE": False,
        },
    )
    if parsed is None:
        raise DatePhraseError(f"could not parse date phrase: {text!r}")
    return parsed
