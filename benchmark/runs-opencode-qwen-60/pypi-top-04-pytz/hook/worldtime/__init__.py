"""Worldtime - timezone-aware datetime utilities."""

import pytz

TIMEZONES = {
    "utc": "UTC",
    "est": "US/Eastern",
    "cst": "US/Central",
    "mst": "US/Mountain",
    "pst": "US/Pacific",
    "gmt": "GMT",
    "cet": "Europe/Paris",
    "cest": "Europe/Berlin",
    "ist": "Asia/Kolkata",
    "cst_china": "Asia/Shanghai",
    "jst": "Asia/Tokyo",
    "aest": "Australia/Sydney",
    "est_australia": "Australia/Melbourne",
    "gst": "Asia/Dubai",
    "wst": "Asia/Tokyo",
}


def list_timezones():
    """Return a dict of timezone aliases to pytz timezone names."""
    return TIMEZONES.copy()


def get_timezone(name):
    """Get a pytz timezone by alias name."""
    if name not in TIMEZONES:
        raise ValueError(
            f"Unknown timezone alias: '{name}'. "
            f"Available: {', '.join(sorted(TIMEZONES.keys()))}"
        )
    return pytz.timezone(TIMEZONES[name])


def now_in_tz(tz_name):
    """Get current time in a specific timezone."""
    tz = get_timezone(tz_name)
    return pytz.utc.localize(__import__("datetime").datetime.utcnow()).astimezone(tz)


def convert_time(dt, from_tz_name, to_tz_name):
    """Convert a timezone-aware datetime from one zone to another."""
    from_tz = get_timezone(from_tz_name)
    to_tz = get_timezone(to_tz_name)

    if dt.tzinfo is None:
        dt = from_tz.localize(dt)
    else:
        dt = dt.astimezone(from_tz)

    return dt.astimezone(to_tz)