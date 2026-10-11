"""Public parsing API.

The parser combines two strategies:

1. A dedicated resolver for ordinal-weekday phrases such as
   ``"the first Monday of next month"`` or ``"last Friday of March 2027"``,
   which generic parsers do not support reliably.
2. :mod:`dateparser` as a fallback for the broad range of other human-written
   strings (``"tomorrow at 5pm"``, ``"in 3 weeks"``, ``"next Friday"`` …).
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, time
from typing import Optional, Union

import dateparser
from dateutil.relativedelta import relativedelta

from .errors import DateParseError
from .ordinals import ORDINALS, WEEKDAYS, nth_weekday_of_month

__all__ = ["parse", "parse_date", "resolve_period"]

_BASE = Union[date, datetime]


def _alternation(options: "dict[str, object]") -> str:
    return "|".join(re.escape(key) for key in sorted(options, key=len, reverse=True))


_ORDINAL_RE = re.compile(
    r"^(?:the\s+)?"
    r"(?P<ordinal>" + _alternation(ORDINALS) + r")\s+"
    r"(?P<weekday>" + _alternation(WEEKDAYS) + r")"
    r"(?:\s+of\s+(?P<period>.+))?$",
    re.IGNORECASE,
)

_MONTHS: "dict[str, int]" = {
    name.lower(): number for number, name in enumerate(calendar.month_name) if name
}
_MONTHS.update(
    {
        abbr.lower(): number
        for number, abbr in enumerate(calendar.month_abbr)
        if abbr
    }
)


def _as_datetime(value: Optional[_BASE]) -> datetime:
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def resolve_period(period: str, base: _BASE) -> "tuple[int, int]":
    """Resolve a period phrase to a ``(year, month)`` pair.

    Supported forms: ``"this month"``, ``"next month"``, ``"last month"``,
    a month name, and a month name followed by a four-digit year.
    """
    text = period.strip().lower()
    if text.startswith("the "):
        text = text[4:].strip()

    relative = re.fullmatch(r"(next|last|previous|this|current)\s+month", text)
    if relative:
        offset = {"next": 1, "last": -1, "previous": -1, "this": 0, "current": 0}
        shifted = _as_datetime(base) + relativedelta(months=offset[relative.group(1)])
        return shifted.year, shifted.month

    named = re.fullmatch(r"([a-z]+)(?:\s+(\d{4}))?", text)
    if named and named.group(1) in _MONTHS:
        year = int(named.group(2)) if named.group(2) else _as_datetime(base).year
        return year, _MONTHS[named.group(1)]

    raise DateParseError(f"unrecognised period: {period!r}")


def _try_ordinal_weekday(text: str, base: _BASE) -> "Optional[date]":
    match = _ORDINAL_RE.match(text.strip())
    if not match:
        return None
    ordinal = ORDINALS[match.group("ordinal").lower()]
    weekday = WEEKDAYS[match.group("weekday").lower()]
    if match.group("period"):
        year, month = resolve_period(match.group("period"), base)
    else:
        current = _as_datetime(base)
        year, month = current.year, current.month
    return nth_weekday_of_month(year, month, weekday, ordinal)


def parse(text: str, *, base: Optional[_BASE] = None) -> datetime:
    """Parse ``text`` into a :class:`datetime.datetime`.

    ``base`` anchors relative expressions and defaults to ``datetime.now()``.
    Raises :class:`DateParseError` when nothing can be understood.
    """
    if text is None or not text.strip():
        raise DateParseError("empty date string")

    base_dt = _as_datetime(base)
    resolved = _try_ordinal_weekday(text, base_dt)
    if resolved is not None:
        return datetime.combine(resolved, time.min)

    parsed = dateparser.parse(
        text,
        settings={
            "RELATIVE_BASE": base_dt,
            "PREFER_DATES_FROM": "future",
        },
    )
    if parsed is None:
        raise DateParseError(f"could not parse date: {text!r}")
    return parsed


def parse_date(text: str, *, base: Optional[_BASE] = None) -> date:
    """Like :func:`parse` but return a :class:`datetime.date`."""
    return parse(text, base=base).date()
