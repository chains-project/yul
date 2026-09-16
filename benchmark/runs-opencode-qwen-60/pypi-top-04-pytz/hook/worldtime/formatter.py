"""Formatting utilities for timezone-aware datetimes."""

from worldtime import get_timezone, TIMEZONES


def format_dt(dt, tz_name, fmt="%Y-%m-%d %H:%M:%S %Z%z"):
    """Format a datetime in a specific timezone with human-readable output."""
    tz = get_timezone(tz_name)
    if dt.tzinfo is None:
        from datetime import datetime
        dt = pytz.utc.localize(datetime.utcnow()).astimezone(tz)
    else:
        dt = dt.astimezone(tz)

    return dt.strftime(fmt)


def format_comparison(dt, tz_names, fmt="%Y-%m-%d %H:%M:%S %Z%z"):
    """Format a datetime across multiple timezones side by side."""
    if dt.tzinfo is None:
        from datetime import datetime
        dt = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.UTC)

    results = {}
    for name in tz_names:
        tz = get_timezone(name)
        converted = dt.astimezone(tz)
        results[name] = converted.strftime(fmt)

    return results