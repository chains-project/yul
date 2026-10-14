"""Parse human-written date expressions relative to a base date.

Free-form parsing is delegated to ``dateparser``. Phrases it doesn't
understand -- "the first Monday of next month", "last Friday" -- are handled
here with ``dateutil.relativedelta``.
"""

from __future__ import annotations

import re
from datetime import datetime

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

_WEEKDAY_RE = "|".join(WEEKDAYS)
_NTH_WEEKDAY_OF = re.compile(
    rf"^(?:the\s+)?(?P<ord>{'|'.join(ORDINALS)})\s+(?P<wd>{_WEEKDAY_RE})\s+(?:of|in)\s+(?P<month>.+)$"
)
_NEXT_LAST_WEEKDAY = re.compile(rf"^(?P<dir>next|last|this)\s+(?P<wd>{_WEEKDAY_RE})$")


class DateParseError(ValueError):
    pass


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _dateparser(text: str, base: datetime) -> datetime | None:
    return dateparser.parse(
        text,
        settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"},
    )


def nth_weekday_of_month(year: int, month: int, weekday: str, n: int) -> datetime:
    """Return the n-th ``weekday`` of the given month; ``n=-1`` means the last one."""
    wd = WEEKDAYS[weekday.lower()]
    first = datetime(year, month, 1)
    if n > 0:
        result = first + relativedelta(weekday=wd(+n))
        if result.month != month:
            raise DateParseError(f"{first:%B %Y} has no #{n} {weekday.capitalize()}")
        return result
    return first + relativedelta(day=31, weekday=wd(-1))


def parse(text: str, base: datetime | None = None) -> datetime:
    """Parse ``text`` into a datetime, resolving relative phrases against ``base``."""
    base = base or datetime.now()
    s = _normalize(text)

    if m := _NTH_WEEKDAY_OF.match(s):
        anchor = base if m["month"] == "this month" else _dateparser(m["month"], base)
        if anchor is None:
            raise DateParseError(f"Could not understand month {m['month']!r}")
        return nth_weekday_of_month(anchor.year, anchor.month, m["wd"], ORDINALS[m["ord"]])

    if m := _NEXT_LAST_WEEKDAY.match(s):
        wd = WEEKDAYS[m["wd"]]
        day = base.replace(hour=0, minute=0, second=0, microsecond=0)
        if m["dir"] == "last":
            return day + relativedelta(days=-1, weekday=wd(-1))
        if m["dir"] == "next":
            return day + relativedelta(days=+1, weekday=wd(+1))
        return day + relativedelta(weekday=wd(+1))  # "this": today or the upcoming one

    result = _dateparser(text, base)
    if result is None:
        raise DateParseError(f"Could not parse date: {text!r}")
    return result
