"""Parse human-written date strings, including relative expressions."""

import re
from datetime import date, datetime

import dateparser
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU, relativedelta

__all__ = ["parse_date", "main"]

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

# e.g. "the first Monday of next month", "last friday in this month",
#      "2nd tuesday of March", "third wed of month after next"
_NTH_WEEKDAY = re.compile(
    r"^(?:the\s+)?(?P<ord>" + "|".join(ORDINALS) + r")\s+"
    r"(?P<wd>" + "|".join(WEEKDAYS) + r")\s+(?:of|in)\s+(?:the\s+)?"
    r"(?P<month>.+?)$",
    re.IGNORECASE,
)


def _resolve_month(spec: str, base: date) -> date | None:
    """Return the first day of the month described by `spec`, or None."""
    spec = spec.strip().lower()
    offsets = {
        "this month": 0, "the month": 0, "month": 0,
        "next month": 1, "last month": -1, "previous month": -1,
        "month after next": 2, "month before last": -2,
    }
    first = base.replace(day=1)
    if spec in offsets:
        return first + relativedelta(months=offsets[spec])
    m = re.fullmatch(r"([a-z]+)(?:\s+(\d{4}))?", spec)
    if m and m.group(1) in MONTHS:
        month = MONTHS[m.group(1)]
        if m.group(2):
            return date(int(m.group(2)), month, 1)
        # Bare month name: the next occurrence, including the current month.
        year = base.year + (1 if month < base.month else 0)
        return date(year, month, 1)
    return None


def _nth_weekday(text: str, base: date) -> date | None:
    m = _NTH_WEEKDAY.match(text.strip())
    if not m:
        return None
    month_start = _resolve_month(m.group("month"), base)
    if month_start is None:
        return None
    n = ORDINALS[m.group("ord").lower()]
    weekday = WEEKDAYS[m.group("wd").lower()]
    if n > 0:
        result = month_start + relativedelta(weekday=weekday(n))
    else:
        # day=31 clamps to the month's last day, then step back to the weekday.
        result = month_start + relativedelta(day=31, weekday=weekday(n))
    if result.month != month_start.month:
        raise ValueError(f"{text!r}: that month has no such weekday")
    return result


def parse_date(text: str, base: date | None = None) -> date:
    """Parse `text` into a date, resolving relative terms against `base`.

    Raises ValueError if the text can't be understood.
    """
    base = base or date.today()
    result = _nth_weekday(text, base)
    if result is not None:
        return result
    parsed = dateparser.parse(
        text,
        settings={
            "RELATIVE_BASE": datetime.combine(base, datetime.min.time()),
            "PREFER_DATES_FROM": "future",
        },
    )
    if parsed is None:
        raise ValueError(f"Could not parse date: {text!r}")
    return parsed.date()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="+", help="date expression to parse")
    parser.add_argument("--base", type=date.fromisoformat,
                        help="reference date (YYYY-MM-DD), default today")
    args = parser.parse_args()
    try:
        print(parse_date(" ".join(args.text), args.base).isoformat())
    except ValueError as e:
        parser.exit(1, f"error: {e}\n")
