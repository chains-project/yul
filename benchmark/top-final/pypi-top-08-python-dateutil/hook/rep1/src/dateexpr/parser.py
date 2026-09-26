"""Flexible date parsing and relative date arithmetic."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

_WEEKDAYS = {
    "monday": MO, "mon": MO,
    "tuesday": TU, "tue": TU, "tues": TU,
    "wednesday": WE, "wed": WE,
    "thursday": TH, "thu": TH, "thurs": TH,
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

_UNITS = {
    "day": "days", "days": "days",
    "week": "weeks", "weeks": "weeks",
    "month": "months", "months": "months",
    "year": "years", "years": "years",
}

_WEEKDAY_NAMES = "|".join(_WEEKDAYS)

_NTH_WEEKDAY_OF_MONTH_RE = re.compile(
    rf"^(?P<ordinal>first|second|third|fourth|fifth|last|1st|2nd|3rd|4th|5th)\s+"
    rf"(?P<weekday>{_WEEKDAY_NAMES})\s+of\s+(?P<month_ref>.+)$",
)

_IN_OFFSET_RE = re.compile(
    r"^in\s+(?P<amount>\d+)\s+(?P<unit>day|days|week|weeks|month|months|year|years)$",
)

_NEXT_LAST_WEEKDAY_RE = re.compile(
    rf"^(?P<direction>next|last)\s+(?P<weekday>{_WEEKDAY_NAMES})$",
)

_SIMPLE_RELATIVE = {
    "today": relativedelta(days=0),
    "tomorrow": relativedelta(days=1),
    "yesterday": relativedelta(days=-1),
    "next week": relativedelta(weeks=1),
    "last week": relativedelta(weeks=-1),
    "next month": relativedelta(months=1),
    "last month": relativedelta(months=-1),
    "next year": relativedelta(years=1),
    "last year": relativedelta(years=-1),
}


def parse_date(text: str, base: Optional[datetime] = None) -> datetime:
    """Parse a flexible, human-written date string relative to ``base``.

    Understands relative phrases (``next friday``, ``in 3 weeks``, ``first
    monday of next month``) as well as anything ``dateutil.parser`` already
    handles (``March 5, 2026``, ``2026-03-05``, ...).
    """
    base = base or datetime.now()
    normalized = text.strip().lower()

    if normalized in _SIMPLE_RELATIVE:
        return base + _SIMPLE_RELATIVE[normalized]

    match = _NTH_WEEKDAY_OF_MONTH_RE.match(normalized)
    if match:
        return _nth_weekday_of_month(
            base,
            _ORDINALS[match.group("ordinal")],
            _WEEKDAYS[match.group("weekday")],
            match.group("month_ref"),
        )

    match = _IN_OFFSET_RE.match(normalized)
    if match:
        kwargs = {_UNITS[match.group("unit")]: int(match.group("amount"))}
        return base + relativedelta(**kwargs)

    match = _NEXT_LAST_WEEKDAY_RE.match(normalized)
    if match:
        weekday = _WEEKDAYS[match.group("weekday")]
        sign = 1 if match.group("direction") == "next" else -1
        return base + relativedelta(weekday=weekday(sign))

    return dateutil_parser.parse(text, default=base, fuzzy=True)


def _resolve_month_start(base: datetime, month_ref: str) -> datetime:
    """Resolve phrases like 'next month', 'this month', 'december' to the
    first day of the referenced month."""
    month_ref = month_ref.strip()
    if month_ref in ("this month", "the current month", "current month"):
        return base.replace(day=1)
    if month_ref == "next month":
        return (base + relativedelta(months=1)).replace(day=1)
    if month_ref == "last month":
        return (base - relativedelta(months=1)).replace(day=1)
    # Falls back to dateutil for month names ("december", "march 2027", ...).
    parsed = dateutil_parser.parse(month_ref, default=base, fuzzy=True)
    return parsed.replace(day=1)


def _nth_weekday_of_month(base: datetime, ordinal: int, weekday, month_ref: str) -> datetime:
    month_start = _resolve_month_start(base, month_ref)
    if ordinal > 0:
        return month_start + relativedelta(day=1, weekday=weekday(ordinal))
    # ordinal == -1 ("last <weekday> of ..."): anchor from month end. day=31
    # clamps to the actual last day of the month.
    month_end = month_start + relativedelta(day=31)
    return month_end + relativedelta(weekday=weekday(-1))
