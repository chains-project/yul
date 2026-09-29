"""Flexible natural-language date parsing and relative date arithmetic.

The :func:`parse_when` entry point understands two broad categories of input:

* **Structured relative expressions** such as ``"the first Monday of next
  month"`` or ``"last day of February 2027"``, which are evaluated with
  :mod:`dateutil.relativedelta`.
* **Human-written dates** such as ``"tomorrow"``, ``"in 3 weeks"``,
  ``"next friday"``, ``"2024-01-05"`` or ``"Jan 5, 2024"``, which are handled
  by :mod:`dateutil.parser` and :mod:`dateparser`.
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Optional, Union

import dateparser
from dateutil import parser as _du_parser
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta

__all__ = ["parse_when", "parse_date", "DateLike"]

DateLike = Union[date, datetime]

# --------------------------------------------------------------------------- #
# Vocabulary
# --------------------------------------------------------------------------- #

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

_MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

_WEEKDAY_ALT = "|".join(sorted(_WEEKDAYS, key=len, reverse=True))
_ORDINAL_ALT = "|".join(sorted(_ORDINALS, key=len, reverse=True))
_MONTH_ALT = "|".join(sorted(_MONTHS, key=len, reverse=True))

_NTH_WEEKDAY_RE = re.compile(
    rf"^(?:the\s+)?(?P<ord>{_ORDINAL_ALT}|\d{{1,2}}(?:st|nd|rd|th))\s+"
    rf"(?P<weekday>{_WEEKDAY_ALT})\s+"
    r"(?:of|in)\s+(?P<month>.+?)\s*$",
    re.IGNORECASE,
)

_DAY_OF_MONTH_RE = re.compile(
    r"^(?:the\s+)?(?P<which>first|last|1st)\s+day\s+(?:of|in)\s+(?P<month>.+?)\s*$",
    re.IGNORECASE,
)

_RELATIVE_WEEKDAY_RE = re.compile(
    rf"^(?:the\s+)?(?P<rel>next|this|coming|last|previous)\s+"
    rf"(?P<weekday>{_WEEKDAY_ALT})\s*$",
    re.IGNORECASE,
)

_MONTH_REF_RE = re.compile(
    rf"^(?:(?P<rel>this|next|last|previous|current)|(?P<offset>\d+)\s+months?\s+(?:from\s+now|ahead|later))?"
    rf"\s*(?:(?P<month>{_MONTH_ALT})|months?)?"
    r"\s*(?P<year>\d{4})?\s*$",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _as_datetime(value: DateLike) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


def _resolve_ordinal(token: str) -> int:
    token = token.lower()
    if token in _ORDINALS:
        return _ORDINALS[token]
    return int(re.sub(r"(st|nd|rd|th)$", "", token))


def _resolve_month_ref(ref: str, base: datetime) -> date:
    """Resolve a month reference to the first day of that month.

    Accepts ``"this month"``, ``"next month"``, ``"last month"``, month names
    (optionally with a relative qualifier like ``"next january"``) and an
    optional explicit four-digit year.
    """
    match = _MONTH_REF_RE.match(ref.strip())
    if not match:
        raise ValueError(f"Unrecognized month reference: {ref!r}")

    rel = (match.group("rel") or "").lower()
    month_name = match.group("month")
    year = int(match.group("year")) if match.group("year") else None

    # "next month" / "this month" / "last month" / "2 months from now".
    if not month_name:
        if match.group("offset"):
            offset = int(match.group("offset"))
            if rel == "last" or "ago" in ref.lower():
                offset = -offset
            return (base + relativedelta(months=offset, day=1)).date()
        if rel in ("this", "current", ""):
            offset = 0
        elif rel == "next":
            offset = 1
        elif rel in ("last", "previous"):
            offset = -1
        else:
            raise ValueError(f"Unrecognized month reference: {ref!r}")
        return (base + relativedelta(months=offset, day=1)).date()

    # A named month, e.g. "january", "next january", "january 2027".
    month = _MONTHS[month_name.lower()]
    if year is None:
        if rel == "next":
            year = base.year + 1 if month <= base.month else base.year
        elif rel in ("last", "previous"):
            year = base.year - 1 if month >= base.month else base.year
        else:
            year = base.year + 1 if month < base.month else base.year
    return date(year, month, 1)


def _nth_weekday(month_start: date, weekday, n: int) -> date:
    """Return the ``n``-th weekday of the month containing ``month_start``.

    ``n`` may be negative, in which case it counts backwards from the end of
    the month (``-1`` is the last such weekday).
    """
    if n > 0:
        return month_start + relativedelta(weekday=weekday(n))
    last_day = month_start + relativedelta(day=31)
    return last_day + relativedelta(weekday=weekday(-1))


def _last_day_of_month(month_start: date) -> date:
    return month_start + relativedelta(day=31)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def parse_when(
    text: str,
    base: Optional[DateLike] = None,
    *,
    default_time: time = time.min,
    settings: Optional[dict] = None,
) -> datetime:
    """Parse a human-written date expression into a :class:`datetime`.

    Args:
        text: The expression to parse, e.g. ``"first Monday of next month"``.
        base: Reference point for relative expressions. Defaults to now. The
            returned value keeps the timezone awareness of ``base``.
        default_time: Time of day used when the expression only names a date.
        settings: Extra ``dateparser`` settings merged over the defaults.

    Raises:
        ValueError: If the expression cannot be understood.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Expected a non-empty date expression")

    base = _as_datetime(base) if base is not None else datetime.now()
    raw = text.strip()
    lowered = raw.lower()

    # 1. "first Monday of next month" style expressions.
    match = _NTH_WEEKDAY_RE.match(lowered)
    if match:
        month_start = _resolve_month_ref(match.group("month"), base)
        weekday = _WEEKDAYS[match.group("weekday").lower()]
        ordinal = _resolve_ordinal(match.group("ord"))
        result = _nth_weekday(month_start, weekday, ordinal)
        return _to_datetime(result, base, default_time)

    # 2. "first day of next month" / "last day of February 2027".
    match = _DAY_OF_MONTH_RE.match(lowered)
    if match:
        month_start = _resolve_month_ref(match.group("month"), base)
        if match.group("which").lower() in ("first", "1st"):
            result = month_start
        else:
            result = _last_day_of_month(month_start)
        return _to_datetime(result, base, default_time)

    # 3. "next friday" / "last monday" (dateparser does not handle these).
    match = _RELATIVE_WEEKDAY_RE.match(lowered)
    if match:
        target = _WEEKDAYS[match.group("weekday").lower()].weekday
        rel = match.group("rel").lower()
        if rel == "next":
            offset = (target - base.weekday()) % 7 or 7
        elif rel in ("this", "coming"):
            offset = (target - base.weekday()) % 7
        else:  # last / previous
            offset = -((base.weekday() - target) % 7 or 7)
        result = (base + timedelta(days=offset)).date()
        return _to_datetime(result, base, default_time)

    # 4. Explicit calendar dates (ISO, "Jan 5 2024", ...).
    try:
        parsed = _du_parser.parse(raw, default=base.replace(
            hour=default_time.hour,
            minute=default_time.minute,
            second=default_time.second,
            microsecond=default_time.microsecond,
        ))
        return parsed
    except (ValueError, OverflowError):
        pass

    # 5. Flexible / relative natural language.
    dateparser_settings = {
        "RELATIVE_BASE": base,
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": base.tzinfo is not None,
        "TIMEZONE": str(base.tzinfo) if base.tzinfo else "UTC",
    }
    if settings:
        dateparser_settings.update(settings)

    parsed = dateparser.parse(raw, settings=dateparser_settings)
    if parsed is None:
        raise ValueError(f"Could not parse date expression: {text!r}")
    return _to_datetime(parsed, base, default_time, keep_parsed_time=True)


def parse_date(
    text: str,
    base: Optional[DateLike] = None,
    **kwargs,
) -> date:
    """Like :func:`parse_when` but returns a :class:`datetime.date`."""
    return parse_when(text, base, **kwargs).date()


def _to_datetime(
    value: DateLike,
    base: datetime,
    default_time: time,
    *,
    keep_parsed_time: bool = False,
) -> datetime:
    if isinstance(value, datetime):
        result = value
        if not keep_parsed_time:
            result = result.replace(
                hour=default_time.hour,
                minute=default_time.minute,
                second=default_time.second,
                microsecond=default_time.microsecond,
            )
    else:
        result = datetime.combine(value, default_time)

    if base.tzinfo is not None and result.tzinfo is None:
        result = result.replace(tzinfo=base.tzinfo)
    return result
