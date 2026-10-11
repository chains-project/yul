"""Parse flexible, human-written date strings and do relative date arithmetic."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Optional, Union

from dateutil.relativedelta import relativedelta

try:  # pragma: no cover - exercised via import guard
    import dateparser
except ImportError:  # pragma: no cover
    dateparser = None

DateLike = Union[date, datetime]

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
}

_WEEKDAYS = {
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

_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


def _alternation(mapping: dict[str, object]) -> str:
    return "|".join(sorted(mapping, key=len, reverse=True))


_NTH_WEEKDAY_RE = re.compile(
    r"^(?:the\s+)?"
    rf"(?P<ordinal>{_alternation(_ORDINALS)})\s+"
    rf"(?P<weekday>{_alternation(_WEEKDAYS)})\b\s+"
    r"(?:of\s+)?"
    r"(?P<period>.+?)\s*$",
    re.IGNORECASE,
)

_RELATIVE_PERIOD_RE = re.compile(
    r"^(?P<direction>next|this|current|last|previous|past)\s+"
    r"(?P<unit>month|year|week)$",
    re.IGNORECASE,
)

_MONTH_YEAR_RE = re.compile(
    rf"^(?P<month>{_alternation(_MONTHS)})(?:\s+(?P<year>\d{{4}}))?$",
    re.IGNORECASE,
)

_YEAR_RE = re.compile(r"^(?P<year>\d{4})$")


def _as_datetime(value: Optional[DateLike]) -> datetime:
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def _month_bounds(anchor: datetime, months: int = 0) -> tuple[datetime, datetime]:
    start = datetime(anchor.year, anchor.month, 1) + relativedelta(months=months)
    return start, start + relativedelta(months=1) - timedelta(days=1)


def _nth_weekday_in_range(
    start: datetime, end: datetime, weekday: int, ordinal: int
) -> datetime:
    if ordinal == -1:
        offset = (end.weekday() - weekday) % 7
        return end - timedelta(days=offset)

    offset = (weekday - start.weekday()) % 7
    result = start + timedelta(days=offset + 7 * (ordinal - 1))
    if result > end:
        raise ValueError(
            f"There is no {ordinal} occurrence of that weekday in the given period"
        )
    return result


def _resolve_period(period: str, base: datetime) -> tuple[datetime, datetime]:
    """Return the inclusive (start, end) range described by ``period``."""
    match = _RELATIVE_PERIOD_RE.match(period)
    if match:
        direction = match.group("direction").lower()
        unit = match.group("unit").lower()
        step = {"next": 1, "this": 0, "current": 0, "last": -1, "previous": -1, "past": -1}[
            direction
        ]

        if unit == "month":
            return _month_bounds(base, step)
        if unit == "year":
            start = datetime(base.year + step, 1, 1)
            return start, start + relativedelta(years=1) - timedelta(days=1)
        # week
        start = datetime.combine(base.date(), time.min) + relativedelta(weeks=step)
        start -= timedelta(days=start.weekday())
        return start, start + timedelta(days=6)

    match = _MONTH_YEAR_RE.match(period)
    if match:
        month = _MONTHS[match.group("month").lower()]
        year_text = match.group("year")
        if year_text:
            year = int(year_text)
        else:
            year = base.year
            if month < base.month:
                year += 1
        return _month_bounds(datetime(year, month, 1))

    match = _YEAR_RE.match(period)
    if match:
        year = int(match.group("year"))
        start = datetime(year, 1, 1)
        return start, start + relativedelta(years=1) - timedelta(days=1)

    raise ValueError(f"Unrecognized period expression: {period!r}")


def _parse_nth_weekday(match: re.Match[str], base: datetime) -> datetime:
    ordinal = _ORDINALS[match.group("ordinal").lower()]
    weekday = _WEEKDAYS[match.group("weekday").lower()]
    start, end = _resolve_period(match.group("period"), base)
    return _nth_weekday_in_range(start, end, weekday, ordinal)


def parse(text: str, base: Optional[DateLike] = None) -> datetime:
    """Parse ``text`` into a :class:`datetime`.

    Supports ordinal weekday phrases (for example ``"the first Monday of next
    month"``, ``"last Friday of this month"``) and falls back to
    ``dateparser`` for other natural-language and absolute date strings.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Date expression must be a non-empty string")

    base_dt = _as_datetime(base)
    match = _NTH_WEEKDAY_RE.match(text.strip())
    if match:
        return _parse_nth_weekday(match, base_dt)

    if dateparser is not None:
        parsed = dateparser.parse(
            text,
            settings={
                "RELATIVE_BASE": base_dt,
                "RETURN_AS_TIMEZONE_AWARE": False,
                "PREFER_DATES_FROM": "future",
            },
        )
        if parsed is not None:
            return parsed

    raise ValueError(f"Could not parse date expression: {text!r}")


def parse_date(text: str, base: Optional[DateLike] = None) -> date:
    """Like :func:`parse` but returns a :class:`datetime.date`."""
    return parse(text, base=base).date()


def shift(value: DateLike, **kwargs: int) -> datetime:
    """Add a relative delta to ``value``.

    Accepts the keyword arguments understood by
    :class:`dateutil.relativedelta.relativedelta`, e.g. ``months=1``,
    ``weeks=2``, ``days=-3``.
    """
    return _as_datetime(value) + relativedelta(**kwargs)
