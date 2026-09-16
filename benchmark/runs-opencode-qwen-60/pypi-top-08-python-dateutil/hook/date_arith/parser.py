"""Parse flexible, human-written date strings and compute relative dates."""

import re
from datetime import datetime, timedelta
from typing import Optional

from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU


WEEKDAY_MAP = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU,
    "mon": MO,
    "tue": TU,
    "wed": WE,
    "thu": TH,
    "fri": FR,
    "sat": SA,
    "sun": SU,
}


RELATIVE_PATTERNS = re.compile(
    r"^(?:the\s+)?(?P<ordinal>first|second|third|fourth|fifth|last|next|previous)\s+(?P<weekday>monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)(?:\s+(?:of\s+)?(?P<period>today|tomorrow|yesterday|this|next|previous|last)\s+(?:month|year|week)?)?\s*$",
    re.IGNORECASE,
)


def parse_date_string(date_string: str, reference: Optional[datetime] = None) -> datetime:
    """Parse a flexible date string and return a datetime.

    Supports patterns like:
    - 'the first Monday of next month'
    - 'next Friday'
    - 'last Tuesday of this month'
    - 'third wed of next year'
    - 'tomorrow', 'yesterday'
    - Standard date strings (delegated to dateutil)

    Args:
        date_string: The human-written date string to parse.
        reference: The reference datetime for relative calculations. Defaults to now.

    Returns:
        The parsed datetime.
    """
    if reference is None:
        reference = datetime.now()

    date_string = date_string.strip()

    # Handle 'tomorrow' and 'yesterday'
    lower = date_string.lower().strip()
    if lower == "tomorrow" or lower == "tomorrow":
        return reference + timedelta(days=1)
    if lower == "yesterday":
        return reference + timedelta(days=-1)
    if lower == "today":
        return reference.replace(hour=0, minute=0, second=0, microsecond=0)

    # Try to match the relative pattern
    match = RELATIVE_PATTERNS.search(date_string)
    if match:
        return _parse_relative_date(match, reference)

    # Fall back to dateutil's parser for standard date strings
    from dateutil import parser as dateutil_parser
    return dateutil_parser.parse(date_string)


def _parse_relative_date(match, reference: datetime) -> datetime:
    """Parse a relative date match and return the computed datetime."""
    ordinal = match.group("ordinal").lower()
    weekday_name = match.group("weekday").lower()
    period = (match.group("period") or "this").lower()

    weekday = WEEKDAY_MAP.get(weekday_name)
    if weekday is None:
        raise ValueError(f"Unknown weekday: {weekday_name}")

    # Determine the base date for the period
    base = _get_period_base(reference, period)

    # Apply ordinal to find the correct occurrence
    return _apply_ordinal(base, weekday, ordinal)


def _get_period_base(reference: datetime, period: str) -> datetime:
    """Get the base date for the given period."""
    period_lower = period.lower()

    if period_lower in ("today", "this"):
        return reference

    if period_lower == "tomorrow":
        return (reference + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    if period_lower == "yesterday":
        return (reference - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    if period_lower == "next":
        # Determine if we're looking at next month or next year
        if "year" in period.lower() or "week" in period.lower():
            return reference.replace(year=reference.year + 1, month=1, day=1,
                                    hour=0, minute=0, second=0, microsecond=0)
        return reference.replace(month=reference.month + 1 if reference.month < 12 else 1,
                                 year=reference.year if reference.month < 12 else reference.year + 1,
                                 day=1, hour=0, minute=0, second=0, microsecond=0)

    if period_lower in ("previous", "last"):
        # Determine if we're looking at previous month or previous year
        if "year" in period.lower():
            return reference.replace(year=reference.year - 1, month=1, day=1,
                                     hour=0, minute=0, second=0, microsecond=0)
        return reference.replace(month=reference.month - 1 if reference.month > 1 else 12,
                                 year=reference.year if reference.month > 1 else reference.year - 1,
                                 day=1, hour=0, minute=0, second=0, microsecond=0)

    # Default to today if period is unrecognized
    return reference


def _apply_ordinal(base: datetime, weekday: int, ordinal: str) -> datetime:
    """Apply the ordinal modifier to find the correct occurrence of a weekday."""
    ordinal_lower = ordinal.lower()

    # Find the first occurrence of the weekday on or after the base date
    days_ahead = weekday.weekday - base.weekday()
    if days_ahead < 0:
        days_ahead += 7
    first_occurrence = base + timedelta(days=days_ahead)

    if ordinal_lower == "first":
        return first_occurrence
    elif ordinal_lower == "second":
        return first_occurrence + timedelta(weeks=1)
    elif ordinal_lower == "third":
        return first_occurrence + timedelta(weeks=2)
    elif ordinal_lower == "fourth":
        return first_occurrence + timedelta(weeks=3)
    elif ordinal_lower == "fifth":
        return first_occurrence + timedelta(weeks=4)
    elif ordinal_lower == "last":
        # Find the last occurrence by starting from the end of the month
        if base.month == 12:
            last_day = base.replace(year=base.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = base.replace(month=base.month + 1, day=1) - timedelta(days=1)

        days_back = last_day.weekday() - weekday.weekday
        if days_back < 0:
            days_back += 7
        return last_day - timedelta(days=days_back)
    elif ordinal_lower == "next":
        return first_occurrence + timedelta(weeks=1)
    elif ordinal_lower == "previous":
        return first_occurrence - timedelta(weeks=1)
    else:
        raise ValueError(f"Unknown ordinal: {ordinal}")