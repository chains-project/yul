"""Core timezone-aware datetime logic.

All public functions work exclusively with *aware* datetimes so that results
are unambiguous regardless of the machine's local timezone.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc

# A handful of representative regions. Keys are stable, human-friendly names;
# values are IANA tz database identifiers understood by zoneinfo.
REGIONS: Dict[str, str] = {
    "utc": "UTC",
    "los_angeles": "America/Los_Angeles",
    "new_york": "America/New_York",
    "sao_paulo": "America/Sao_Paulo",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "lagos": "Africa/Lagos",
    "johannesburg": "Africa/Johannesburg",
    "dubai": "Asia/Dubai",
    "kolkata": "Asia/Kolkata",
    "shanghai": "Asia/Shanghai",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "auckland": "Pacific/Auckland",
}


def resolve_zone(name: str) -> ZoneInfo:
    """Return a ``ZoneInfo`` for an IANA name or a friendly region key.

    Raises:
        KeyError: if a friendly region key is unknown.
        zoneinfo.ZoneInfoNotFoundError: if the IANA identifier is unknown.
    """
    tz_name = REGIONS.get(name.lower(), name)
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ZoneInfoNotFoundError(
            f"Unknown timezone {name!r}. Use an IANA name such as "
            f"'Europe/Paris' or one of: {', '.join(sorted(REGIONS))}"
        ) from exc


def now() -> datetime:
    """Return the current time as an aware UTC datetime."""
    return datetime.now(UTC)


def now_in(name: str) -> datetime:
    """Return the current time in the given timezone."""
    return datetime.now(resolve_zone(name))


def parse_datetime(text: str, name: str = "UTC") -> datetime:
    """Parse an ISO-8601 string into an aware datetime.

    The input is interpreted in ``name``'s timezone. If the text already carries
    a UTC offset that offset wins; otherwise the zone is attached.
    """
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(
            f"Could not parse {text!r} as ISO-8601 (e.g. '2026-09-29 14:30')"
        ) from exc

    if parsed.tzinfo is not None:
        return parsed
    return parsed.replace(tzinfo=resolve_zone(name))


def convert(moment: datetime, name: str) -> datetime:
    """Convert an aware datetime to another timezone.

    Raises:
        ValueError: if ``moment`` is naive (has no tzinfo), which would make the
            conversion ambiguous.
    """
    if moment.tzinfo is None:
        raise ValueError(
            "Cannot convert a naive datetime. Attach a timezone first, "
            "e.g. via parse_datetime(...)."
        )
    return moment.astimezone(resolve_zone(name))


def format_in_zone(moment: datetime, name: str, fmt: str = "%Y-%m-%d %H:%M %Z") -> str:
    """Format an aware datetime in the given timezone."""
    return convert(moment, name).strftime(fmt)


def local_times(
    at: Optional[datetime] = None,
    names: Optional[Iterable[str]] = None,
    fmt: str = "%Y-%m-%d %H:%M %Z",
) -> List[tuple]:
    """Pair each region name with the given moment rendered in its timezone."""
    moment = at or now()
    zones = list(names) if names is not None else list(REGIONS)
    return [(name, format_in_zone(moment, name, fmt)) for name in zones]
