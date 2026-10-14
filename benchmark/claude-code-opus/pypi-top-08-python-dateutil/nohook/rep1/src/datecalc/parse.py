"""Date resolution.

dateparser handles most free-form input ("tomorrow", "in 3 days",
"March 5 2027", "2 weeks ago"), but it does not understand ordinal-weekday
phrases ("first Monday of next month") or "next/last <weekday>". Those are
handled here with dateutil's relativedelta before falling back to dateparser.
"""

import re
from datetime import date

import dateparser
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta

WEEKDAYS = {
    "monday": MO, "mon": MO,
    "tuesday": TU, "tue": TU, "tues": TU,
    "wednesday": WE, "wed": WE,
    "thursday": TH, "thu": TH, "thur": TH, "thurs": TH,
    "friday": FR, "fri": FR,
    "saturday": SA, "sat": SA,
    "sunday": SU, "sun": SU,
}

ORDINALS = {
    "first": 1, "1st": 1,
    "second": 2, "2nd": 2,
    "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4,
    "fifth": 5, "5th": 5,
    "last": -1,
}

_WD = "|".join(sorted(WEEKDAYS, key=len, reverse=True))
_ORD = "|".join(ORDINALS)

# "the first monday of next month", "last fri in march 2027"
ORDINAL_WEEKDAY_RE = re.compile(
    rf"^(?:the\s+)?(?P<ord>{_ORD})\s+(?P<wd>{_WD})\s+(?:of|in)\s+(?P<month>.+)$"
)
# "next friday", "last tue", "this sunday"
RELATIVE_WEEKDAY_RE = re.compile(rf"^(?P<rel>next|last|this)\s+(?P<wd>{_WD})$")


class DateParseError(ValueError):
    pass


def resolve(text: str, base: date | None = None) -> date:
    """Resolve a human-written date expression to a date, relative to `base`
    (default: today)."""
    base = base or date.today()
    normalized = " ".join(text.lower().split()).rstrip(".")

    if m := ORDINAL_WEEKDAY_RE.match(normalized):
        month_start = _resolve_month(m["month"], base)
        return nth_weekday_of_month(
            month_start.year, month_start.month, WEEKDAYS[m["wd"]], ORDINALS[m["ord"]]
        )

    if m := RELATIVE_WEEKDAY_RE.match(normalized):
        return _relative_weekday(m["rel"], WEEKDAYS[m["wd"]], base)

    return _dateparser(normalized, base)


def nth_weekday_of_month(year: int, month: int, weekday, n: int) -> date:
    """The nth `weekday` (a dateutil weekday such as MO) of the given month.
    n=-1 means the last one. Raises DateParseError if it doesn't exist
    (e.g. a fifth Monday in a month that has only four)."""
    if n > 0:
        result = date(year, month, 1) + relativedelta(weekday=weekday(+n))
    else:
        result = date(year, month, 1) + relativedelta(day=31, weekday=weekday(n))
    if result.month != month:
        raise DateParseError(f"There is no #{n} {weekday} in {year}-{month:02d}")
    return result


def _relative_weekday(rel: str, weekday, base: date) -> date:
    # "next X" = first X strictly after base; "last X" = most recent X strictly
    # before base; "this X" = X in the current Mon-Sun week.
    if rel == "next":
        return base + relativedelta(days=+1, weekday=weekday(+1))
    if rel == "last":
        return base + relativedelta(days=-1, weekday=weekday(-1))
    monday = base + relativedelta(weekday=MO(-1))
    return monday + relativedelta(weekday=weekday(+1))


def _resolve_month(expr: str, base: date) -> date:
    """Return the first day of the month described by `expr`."""
    expr = expr.strip()
    fixed = {"this month": 0, "next month": 1, "last month": -1}
    if expr in fixed:
        return base + relativedelta(months=fixed[expr], day=1)
    if m := re.fullmatch(r"(?:in\s+)?(\d+)\s+months?(?:\s+from\s+now)?", expr):
        return base + relativedelta(months=int(m[1]), day=1)
    return _dateparser(expr, base, prefer_day="first").replace(day=1)


def _dateparser(text: str, base: date, prefer_day: str = "current") -> date:
    from datetime import datetime

    parsed = dateparser.parse(
        text,
        languages=["en"],
        settings={
            "RELATIVE_BASE": datetime.combine(base, datetime.min.time()),
            "PREFER_DATES_FROM": "future",
            "PREFER_DAY_OF_MONTH": prefer_day,
        },
    )
    if parsed is None:
        raise DateParseError(f"Could not understand date: {text!r}")
    return parsed.date()
