"""Date parsing.

Two layers:

1. A small grammar for weekday expressions that general-purpose
   parsers don't handle, e.g. "the first Monday of next month" or
   "last Friday of December 2026", plus "next/last/this <weekday>".
   Arithmetic is done with ``dateutil.relativedelta``.
2. A fallback to ``dateparser`` for everything else: "tomorrow",
   "in 3 weeks", "12 Jan 2027", "2026-11-05", etc.
"""

from __future__ import annotations

import re
from datetime import date, datetime

import dateparser
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta

WEEKDAYS = {
    "monday": MO, "tuesday": TU, "wednesday": WE, "thursday": TH,
    "friday": FR, "saturday": SA, "sunday": SU,
}
ORDINALS = {
    "first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4, "fifth": 5, "5th": 5, "last": -1,
}
MONTHS = {
    name: i
    for i, names in enumerate(
        [("january", "jan"), ("february", "feb"), ("march", "mar"),
         ("april", "apr"), ("may",), ("june", "jun"), ("july", "jul"),
         ("august", "aug"), ("september", "sep", "sept"),
         ("october", "oct"), ("november", "nov"), ("december", "dec")],
        start=1,
    )
    for name in names
}

_ORDINAL_WEEKDAY_RE = re.compile(
    rf"""^\s*(?:the\s+)?
    (?P<ordinal>{"|".join(ORDINALS)})\s+
    (?P<weekday>{"|".join(WEEKDAYS)})\s+
    (?:of|in)\s+
    (?:
        (?P<relative>this|next|last)\s+month
      | (?P<month>{"|".join(sorted(MONTHS, key=len, reverse=True))})\.?(?:\s+(?P<year>\d{{4}}))?
    )\s*$""",
    re.IGNORECASE | re.VERBOSE,
)


_RELATIVE_WEEKDAY_RE = re.compile(
    rf"^\s*(?P<relative>this|next|last)\s+(?P<weekday>{"|".join(WEEKDAYS)})\s*$",
    re.IGNORECASE,
)


class DateParseError(ValueError):
    """Raised when a string can't be interpreted as a date."""


def parse_date(text: str, today: date | None = None) -> date:
    """Parse ``text`` into a ``date``, relative to ``today`` (default: now)."""
    today = today or date.today()

    for special in (_parse_ordinal_weekday, _parse_relative_weekday):
        result = special(text, today)
        if result is not None:
            return result

    parsed = dateparser.parse(
        text,
        settings={
            "RELATIVE_BASE": datetime.combine(today, datetime.min.time()),
            "PREFER_DATES_FROM": "future",
        },
    )
    if parsed is None:
        raise DateParseError(f"Could not parse date: {text!r}")
    return parsed.date()


def _parse_relative_weekday(text: str, today: date) -> date | None:
    """"this/next/last <weekday>".

    "next" and "last" are strictly after/before today; "this" may be today.
    """
    m = _RELATIVE_WEEKDAY_RE.match(text)
    if not m:
        return None
    weekday = WEEKDAYS[m["weekday"].lower()]
    match m["relative"].lower():
        case "this":
            return today + relativedelta(weekday=weekday(+1))
        case "next":
            return today + relativedelta(days=1, weekday=weekday(+1))
        case _:
            return today + relativedelta(days=-1, weekday=weekday(-1))


def _parse_ordinal_weekday(text: str, today: date) -> date | None:
    m = _ORDINAL_WEEKDAY_RE.match(text)
    if not m:
        return None

    n = ORDINALS[m["ordinal"].lower()]
    weekday = WEEKDAYS[m["weekday"].lower()]

    if m["relative"]:
        offset = {"last": -1, "this": 0, "next": 1}[m["relative"].lower()]
        month_start = today.replace(day=1) + relativedelta(months=offset)
    else:
        month = MONTHS[m["month"].lower()]
        if m["year"]:
            year = int(m["year"])
        else:
            # Bare month name: pick the next occurrence (this month counts).
            year = today.year if month >= today.month else today.year + 1
        month_start = date(year, month, 1)

    if n == -1:
        # Jump to the last day of the month, then step back to the weekday.
        result = month_start + relativedelta(day=31, weekday=weekday(-1))
    else:
        result = month_start + relativedelta(weekday=weekday(n))
        if result.month != month_start.month:
            raise DateParseError(
                f"{month_start:%B %Y} has no {m['ordinal']} {m['weekday']}"
            )
    return result
