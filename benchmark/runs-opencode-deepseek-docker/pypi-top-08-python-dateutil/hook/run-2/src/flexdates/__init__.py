"""Flexible parsing of human-written date strings and relative date arithmetic."""

from __future__ import annotations

import re
from datetime import date, datetime

import dateparser
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta
from dateutil.rrule import MONTHLY, rrule

__all__ = [
    "parse_date",
    "add_relative",
    "nth_weekday_of_month",
    "resolve",
]

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


def _alternation(values):
    return "|".join(sorted(values, key=len, reverse=True))


_NTH_WEEKDAY_RE = re.compile(
    r"^\s*(?:the\s+)?(?P<ordinal>{ordinals})"
    r"\s+(?P<weekday>{weekdays})"
    r"(?:\s+of\s+(?P<month>.+?))?\s*$".format(
        ordinals=_alternation(_ORDINALS),
        weekdays=_alternation(_WEEKDAYS),
    ),
    re.IGNORECASE,
)


def _coerce_base(base):
    if base is None:
        return datetime.now()
    if isinstance(base, datetime):
        return base
    if isinstance(base, date):
        return datetime(base.year, base.month, base.day)
    raise TypeError("base must be a datetime, date, or None")


def parse_date(text, base=None, **settings):
    """Parse a flexible, human-written date string.

    Wraps :func:`dateparser.parse`, using ``base`` as the reference point for
    relative expressions such as ``"tomorrow"`` or ``"3 weeks ago"``.

    Raises:
        ValueError: if ``text`` is empty or cannot be parsed.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")

    opts = {"RELATIVE_BASE": _coerce_base(base)}
    opts.update(settings)
    result = dateparser.parse(text, settings=opts)
    if result is None:
        raise ValueError(f"could not parse date string: {text!r}")
    return result


def add_relative(base, **delta):
    """Add a relative delta to ``base``.

    Accepts ``python-dateutil`` :class:`relativedelta` keyword arguments, e.g.
    ``add_relative(now, months=+1, days=-3)``.
    """
    return _coerce_base(base) + relativedelta(**delta)


def nth_weekday_of_month(year, month, weekday, n):
    """Return the ``n``th ``weekday`` of a given month.

    ``n`` is 1-based; use ``-1`` for the last occurrence. ``weekday`` may be a
    name (``"monday"``) or a ``dateutil`` weekday object (``MO``).
    """
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    if isinstance(weekday, str):
        try:
            weekday = _WEEKDAYS[weekday.lower()]
        except KeyError:
            raise ValueError(f"unknown weekday: {weekday!r}") from None

    occurrences = list(
        rrule(MONTHLY, dtstart=datetime(year, month, 1), byweekday=weekday, bysetpos=n, count=1)
    )
    if not occurrences:
        raise ValueError(f"no {weekday} #{n} in {year}-{month:02d}")
    return occurrences[0]


def resolve(text, base=None, **settings):
    """Resolve ``text`` to a datetime, handling weekday-of-month phrases.

    Supports expressions such as ``"the first Monday of next month"`` in
    addition to everything :func:`parse_date` accepts. ``base`` anchors all
    relative expressions.
    """
    base_dt = _coerce_base(base)
    match = _NTH_WEEKDAY_RE.match(text)
    if match:
        ordinal = _ORDINALS[match.group("ordinal").lower()]
        month_text = match.group("month")
        anchor = parse_date(month_text, base=base_dt, **settings) if month_text else base_dt
        return nth_weekday_of_month(
            anchor.year, anchor.month, match.group("weekday"), ordinal
        )
    return parse_date(text, base=base_dt, **settings)
