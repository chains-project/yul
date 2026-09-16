"""Timezone-aware datetime utilities using pytz."""

from datetime import datetime
from typing import List, Optional

import pytz


# Common world timezones
WORLD_TIMEZONES = [
    "UTC",
    "US/Eastern",
    "US/Pacific",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
    "America/Sao_Paulo",
    "Pacific/Auckland",
]


def utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(pytz.utc)


def now_in_tz(tz_name: str) -> datetime:
    """Return the current time in a specified timezone.

    Args:
        tz_name: IANA timezone name (e.g. 'US/Eastern', 'Europe/London').

    Returns:
        Timezone-aware datetime for the specified timezone.

    Raises:
        pytz.UnknownTimeZoneError: If the timezone name is not recognized.
    """
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)


def convert_time(dt: datetime, from_tz_name: str, to_tz_name: str) -> datetime:
    """Convert a timezone-aware datetime from one timezone to another.

    Args:
        dt: Timezone-aware datetime.
        from_tz_name: Source IANA timezone name.
        to_tz_name: Target IANA timezone name.

    Returns:
        Datetime in the target timezone.

    Raises:
        ValueError: If dt is naive (not timezone-aware).
        pytz.UnknownTimeZoneError: If either timezone name is not recognized.
    """
    if dt.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware.")

    to_tz = pytz.timezone(to_tz_name)
    return dt.astimezone(to_tz)


def create_aware(year: int, month: int, day: int, hour: int = 0,
                 minute: int = 0, second: int = 0,
                 tz_name: str = "UTC") -> datetime:
    """Create a timezone-aware datetime.

    Args:
        year, month, day: Date components.
        hour, minute, second: Time components (default midnight).
        tz_name: IANA timezone name (default UTC).

    Returns:
        Timezone-aware datetime.
    """
    tz = pytz.timezone(tz_name)
    dt = datetime(year, month, day, hour, minute, second)
    return tz.localize(dt)


def format_dt(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z%z") -> str:
    """Format a timezone-aware datetime.

    Args:
        dt: Timezone-aware datetime.
        fmt: strftime format string (default: 'YYYY-MM-DD HH:MM:SS TZOFFSET').

    Returns:
        Formatted datetime string.
    """
    return dt.strftime(fmt)


def world_clock_display(tz_names: Optional[List[str]] = None) -> str:
    """Display current times across multiple timezones.

    Args:
        tz_names: List of timezone names to display. Defaults to WORLD_TIMEZONES.

    Returns:
        Multi-line string with current times in each timezone.
    """
    if tz_names is None:
        tz_names = WORLD_TIMEZONES

    lines = ["World Clock (UTC now: " + format_dt(utc_now()) + ")"]
    lines.append("-" * 60)

    utc = utc_now()
    for tz_name in sorted(tz_names):
        local_time = convert_time(utc, "UTC", tz_name)
        lines.append(f"  {tz_name:25s} {format_dt(local_time)}")

    return "\n".join(lines)