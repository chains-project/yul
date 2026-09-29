"""Flexible date-string parsing and relative date arithmetic.

The parser handles two broad categories of phrases:

* Natural-language dates understood by ``dateparser`` (e.g. ``"in 3 days"``,
  ``"2 weeks ago"``, ``"tomorrow"``, ``"January 2027"``).
* Structural relative phrases the underlying library does not cover, such as
  ``"the first Monday of next month"`` or ``"last Friday of this month"``.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, time, timedelta
from typing import Optional, Union

import dateparser
from dateutil.relativedelta import relativedelta
from dateutil.rrule import FR, MO, SA, SU, TH, TU, WE

DateLike = Union[date, datetime]

_WEEKDAYS = {
    "monday": MO,
    "mon": MO,
    "tuesday": TU,
    "tue": TU,
    "tues": TU,
    "wednesday": WE,
    "wed": WE,
    "thursday": TH,
    "thu": TH,
    "thur": TH,
    "thurs": TH,
    "friday": FR,
    "fri": FR,
    "saturday": SA,
    "sat": SA,
    "sunday": SU,
    "sun": SU,
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
}

_WEEKDAY_PATTERN = "|".join(sorted(_WEEKDAYS, key=len, reverse=True))

_NTH_WEEKDAY_RE = re.compile(
    r"^(?P<ordinal>first|second|third|fourth|fifth|last|\d+(?:st|nd|rd|th))\s+"
    r"(?P<weekday>" + _WEEKDAY_PATTERN + r")"
    r"\s+of\s+(?P<anchor>.+)$",
    re.IGNORECASE,
)

_RELATIVE_WEEKDAY_RE = re.compile(
    r"^(?P<which>this|next|last)\s+(?P<weekday>" + _WEEKDAY_PATTERN + r")$",
    re.IGNORECASE,
)

_RELATIVE_PERIOD_RE = re.compile(
    r"^(?P<which>this|next|last)\s+(?P<period>month|year|week|day)$",
    re.IGNORECASE,
)

_DATEPARSER_SETTINGS = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": False,
}


def _to_datetime(value: DateLike) -> datetime:
    """Normalise a ``date``/``datetime`` to a ``datetime`` (midnight for dates)."""
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time())


def _relative_period(base: datetime, which: str, period: str) -> datetime:
    """Shift ``base`` by a whole ``period`` in the requested direction."""
    if which == "this":
        return base
    sign = 1 if which == "next" else -1
    return base + relativedelta(**{period + "s": sign})


def _parse_anchor(text: str, base: datetime) -> Optional[datetime]:
    """Resolve the ``... of <anchor>`` part of an nth-weekday phrase."""
    text = text.strip().lower()
    match = _RELATIVE_PERIOD_RE.match(text)
    if match:
        return _relative_period(base, match.group("which"), match.group("period"))
    return dateparser.parse(text, settings={**_DATEPARSER_SETTINGS, "RELATIVE_BASE": base})


def nth_weekday_of_month(
    year: int,
    month: int,
    weekday: Union[str, object],
    n: int,
) -> Optional[datetime]:
    """Return the ``n``-th ``weekday`` of ``month``.

    ``n`` may be negative to count from the end of the month (``-1`` is the
    last occurrence). Returns ``None`` when the occurrence does not exist,
    e.g. a fifth Monday in a month that has only four.
    """
    if isinstance(weekday, str):
        weekday = _WEEKDAYS[weekday.lower()]
    if n == 0:
        raise ValueError("n must be non-zero")
    target = weekday.weekday
    if n > 0:
        first = date(year, month, 1)
        offset = (target - first.weekday()) % 7
        candidate = first + timedelta(days=offset + (n - 1) * 7)
    else:
        last = date(year, month, calendar.monthrange(year, month)[1])
        offset = (last.weekday() - target) % 7
        candidate = last - timedelta(days=offset + (abs(n) - 1) * 7)
    if candidate.year != year or candidate.month != month:
        return None
    return datetime.combine(candidate, time())


def relative_weekday(base: DateLike, weekday: Union[str, object], which: str = "next") -> datetime:
    """Resolve a relative weekday such as ``next Monday`` or ``last Friday``.

    ``next``/``last`` always move at least one day; ``this`` returns ``base``
    when it already falls on the requested weekday.
    """
    base = _to_datetime(base)
    if isinstance(weekday, str):
        weekday = _WEEKDAYS[weekday.lower()]
    target = weekday.weekday
    today = base.weekday()
    if which == "next":
        delta = (target - today) % 7 or 7
    elif which == "last":
        delta = -((today - target) % 7 or 7)
    elif which == "this":
        delta = (target - today) % 7
    else:
        raise ValueError("which must be 'this', 'next' or 'last'")
    return base + timedelta(days=delta)


def parse(text: str, base: Optional[DateLike] = None) -> Optional[datetime]:
    """Parse ``text`` into a ``datetime`` relative to ``base``.

    ``base`` defaults to ``datetime.now()``. Returns ``None`` when the phrase
    cannot be understood.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    base_dt = _to_datetime(base) if base is not None else datetime.now()
    phrase = text.strip().rstrip(".").lower()
    if phrase.startswith("the "):
        phrase = phrase[4:].strip()

    match = _NTH_WEEKDAY_RE.match(phrase)
    if match:
        anchor = _parse_anchor(match.group("anchor"), base_dt)
        if anchor is None:
            return None
        ordinal = _ORDINALS[match.group("ordinal").lower()]
        weekday = _WEEKDAYS[match.group("weekday").lower()]
        result = nth_weekday_of_month(anchor.year, anchor.month, weekday, ordinal)
        if result is None:
            return None
        return result.replace(
            hour=base_dt.hour,
            minute=base_dt.minute,
            second=base_dt.second,
            microsecond=base_dt.microsecond,
        )

    match = _RELATIVE_WEEKDAY_RE.match(phrase)
    if match:
        return relative_weekday(base_dt, match.group("weekday"), match.group("which"))

    match = _RELATIVE_PERIOD_RE.match(phrase)
    if match:
        return _relative_period(base_dt, match.group("which"), match.group("period"))

    return dateparser.parse(phrase, settings={**_DATEPARSER_SETTINGS, "RELATIVE_BASE": base_dt})


def parse_date(text: str, base: Optional[DateLike] = None) -> Optional[date]:
    """Like :func:`parse` but returns a :class:`datetime.date`."""
    result = parse(text, base=base)
    return result.date() if result is not None else None
