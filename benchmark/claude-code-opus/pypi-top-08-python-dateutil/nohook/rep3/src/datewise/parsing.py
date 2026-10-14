"""Parse flexible, human-written date expressions into concrete dates."""

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
    for i, name in enumerate(
        ["january", "february", "march", "april", "may", "june", "july",
         "august", "september", "october", "november", "december"],
        start=1,
    )
}

# "the first Monday of next month", "last friday in this month",
# "2nd tuesday of march", "third thursday of november 2027"
_NTH_WEEKDAY = re.compile(
    rf"^(?:the\s+)?(?P<ord>{'|'.join(ORDINALS)})\s+"
    rf"(?P<wd>{'|'.join(WEEKDAYS)})\s+(?:of|in)\s+(?P<month>.+)$",
    re.IGNORECASE,
)


class DateParseError(ValueError):
    """Raised when an expression cannot be interpreted as a date."""


def nth_weekday(year: int, month: int, n: int, weekday: str) -> date:
    """Return the nth (1-5, or -1 for last) given weekday of a month."""
    wd = WEEKDAYS[weekday.lower()]
    first = date(year, month, 1)
    if n == -1:
        result = first + relativedelta(day=31, weekday=wd(-1))
    else:
        result = first + relativedelta(weekday=wd(n))
    if result.month != month:
        raise DateParseError(f"{year}-{month:02d} has no {n}th {weekday}")
    return result


def _resolve_month(text: str, today: date) -> tuple[int, int]:
    """Resolve 'next month', 'this month', 'last month', 'march', 'march 2027'."""
    text = text.strip().lower()
    relative = {"this month": 0, "next month": 1, "last month": -1, "previous month": -1}
    if text in relative:
        target = today + relativedelta(months=relative[text])
        return target.year, target.month

    match = re.fullmatch(r"(?:next\s+)?([a-z]+)(?:\s+(\d{4}))?", text)
    if match and match.group(1) in MONTHS:
        month = MONTHS[match.group(1)]
        if match.group(2):
            return int(match.group(2)), month
        # A bare month name means its next occurrence (including the current month).
        year = today.year if month >= today.month else today.year + 1
        if text.startswith("next ") and month == today.month:
            year += 1
        return year, month

    raise DateParseError(f"Unrecognised month expression: {text!r}")


def parse_date(text: str, today: date | None = None) -> date:
    """Parse a human-written date expression relative to ``today``.

    Handles "Nth weekday of <month>" phrases directly and delegates everything
    else ("tomorrow", "in 3 weeks", "next friday", "2026-12-25", ...) to dateparser.
    """
    today = today or date.today()
    text = text.strip()

    if match := _NTH_WEEKDAY.match(text):
        year, month = _resolve_month(match["month"], today)
        return nth_weekday(year, month, ORDINALS[match["ord"].lower()], match["wd"])

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
