"""Core parsing engine for :mod:`dateflex`."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Final

import dateparser
from dateutil.relativedelta import relativedelta

__all__ = ["DateParseError", "parse", "parse_date", "shift"]


class DateParseError(ValueError):
    """Raised when a date expression cannot be understood."""


_WEEKDAYS: Final[dict[str, int]] = {
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

_ORDINALS: Final[dict[str, int]] = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "last": -1,
}

_WEEKDAY_ALT = "|".join(sorted(_WEEKDAYS, key=len, reverse=True))

_ORDINAL_WEEKDAY_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:the\s+)?(?P<ordinal>first|second|third|fourth|fifth|last|\d{1,2}(?:st|nd|rd|th))"
    r"\s+(?P<weekday>[a-z]+)\s+of\s+(?:the\s+)?(?P<anchor>.+?)$",
    re.IGNORECASE,
)

_WEEKDAY_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?:(?P<qualifier>next|this|coming|last|previous|past)\s+)?"
    rf"(?P<weekday>{_WEEKDAY_ALT})"
    rf"(?:\s+(?P<time>at\s+.+|\d.*))?$",
    re.IGNORECASE,
)

_DAY_KEYWORDS: Final[dict[str, int]] = {
    "today": 0,
    "now": 0,
    "tomorrow": 1,
    "tmr": 1,
    "yesterday": -1,
}


def parse(text: str | date | datetime, base: date | datetime | None = None) -> datetime:
    """Parse a human-written date expression into a :class:`datetime.datetime`.

    Relative expressions (``"tomorrow"``, ``"next friday"``) and ordinal
    expressions (``"the first Monday of next month"``) are resolved against
    *base*, which defaults to :func:`datetime.now`.

    The time of day defaults to the base time for relative expressions and to
    midnight for absolute ones.
    """
    if isinstance(text, datetime):
        return text
    if isinstance(text, date):
        return datetime.combine(text, time())
    if not isinstance(text, str):
        raise TypeError(f"expected a string or date, got {type(text).__name__}")

    base_dt = _as_datetime(base) if base is not None else datetime.now()
    normalized = " ".join(text.strip().split())
    if not normalized:
        raise DateParseError("empty date expression")

    for parser in (_parse_day_keyword, _parse_ordinal_weekday, _parse_relative_weekday):
        result = parser(normalized, base_dt)
        if result is not None:
            return result

    parsed: datetime | None = dateparser.parse(normalized, settings={"RELATIVE_BASE": base_dt})
    if parsed is None:
        raise DateParseError(f"could not parse date expression: {text!r}")
    return parsed


def parse_date(text: str | date | datetime, base: date | datetime | None = None) -> date:
    """Like :func:`parse`, but return a :class:`datetime.date`."""
    return parse(text, base).date()


def shift(
    base: str | date | datetime,
    *,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """Add a relative delta to *base* using calendar-aware arithmetic.

    Adding one month to January 31 yields the end of February rather than an
    invalid date, matching :class:`dateutil.relativedelta.relativedelta`.
    """
    reference = _as_datetime(base)
    result: datetime = reference + relativedelta(
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )
    return result


def _as_datetime(value: str | date | datetime) -> datetime:
    if isinstance(value, str):
        return parse(value)
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time())


def _at_time(day: date, base: datetime) -> datetime:
    return datetime(
        day.year,
        day.month,
        day.day,
        base.hour,
        base.minute,
        base.second,
        base.microsecond,
        tzinfo=base.tzinfo,
    )


def _parse_day_keyword(text: str, base: datetime) -> datetime | None:
    offset = _DAY_KEYWORDS.get(text.lower())
    if offset is None:
        return None
    return base + timedelta(days=offset)


def _parse_ordinal_weekday(text: str, base: datetime) -> datetime | None:
    match = _ORDINAL_WEEKDAY_RE.match(text)
    if match is None:
        return None
    weekday = _WEEKDAYS.get(match.group("weekday").lower())
    if weekday is None:
        return None
    ordinal = _parse_ordinal(match.group("ordinal"))
    year, month = _resolve_month(match.group("anchor"), base)
    day = _nth_weekday(year, month, weekday, ordinal)
    if day is None:
        raise DateParseError(
            f"there is no {match.group('ordinal')} {match.group('weekday')} "
            f"in {match.group('anchor')!r}"
        )
    return _at_time(day, base)


def _parse_ordinal(token: str) -> int:
    lowered = token.lower()
    if lowered in _ORDINALS:
        return _ORDINALS[lowered]
    value = int(re.sub(r"\D", "", lowered))
    if not 1 <= value <= 5:
        raise DateParseError(f"unsupported ordinal: {token!r}")
    return value


def _resolve_month(anchor: str, base: datetime) -> tuple[int, int]:
    key = anchor.strip().lower().removeprefix("the ").strip()
    offsets = {
        "this month": 0,
        "current month": 0,
        "next month": 1,
        "last month": -1,
        "previous month": -1,
        "month after next": 2,
        "month before last": -2,
    }
    if key in offsets:
        reference: datetime = base + relativedelta(months=offsets[key])
        return reference.year, reference.month

    parsed: datetime | None = dateparser.parse(anchor, settings={"RELATIVE_BASE": base})
    if parsed is None:
        raise DateParseError(f"could not resolve month reference: {anchor!r}")
    return parsed.year, parsed.month


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date | None:
    first = date(year, month, 1)
    if n == -1:
        next_month = date(year + (month == 12), month % 12 + 1, 1)
        last = next_month - timedelta(days=1)
        return last - timedelta(days=(last.weekday() - weekday) % 7)
    candidate = first + timedelta(days=(weekday - first.weekday()) % 7 + (n - 1) * 7)
    return candidate if candidate.month == month else None


def _parse_relative_weekday(text: str, base: datetime) -> datetime | None:
    match = _WEEKDAY_RE.match(text)
    if match is None:
        return None
    weekday = _WEEKDAYS.get(match.group("weekday").lower())
    if weekday is None:
        return None

    qualifier = (match.group("qualifier") or "").lower()
    delta = (weekday - base.weekday()) % 7
    if qualifier in {"next", "coming"}:
        delta = delta or 7
    elif qualifier in {"last", "previous", "past"}:
        delta = -((base.weekday() - weekday) % 7 or 7)

    target = _at_time((base + timedelta(days=delta)).date(), base)
    time_clause = match.group("time")
    if time_clause:
        return _apply_time_clause(target, time_clause)
    return target


def _apply_time_clause(target: datetime, time_clause: str) -> datetime:
    parsed: datetime | None = dateparser.parse(time_clause, settings={"RELATIVE_BASE": target})
    if parsed is None:
        raise DateParseError(f"could not parse time: {time_clause!r}")
    return target.replace(
        hour=parsed.hour,
        minute=parsed.minute,
        second=parsed.second,
        microsecond=parsed.microsecond,
    )
