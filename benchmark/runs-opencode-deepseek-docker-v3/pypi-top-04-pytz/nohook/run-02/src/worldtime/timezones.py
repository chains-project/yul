"""Timezone-aware datetime helpers for working across world regions.

The guiding rule is simple: an aware datetime identifies an *instant*, a
naive datetime does not. Every helper here either produces or requires an
aware value, so callers never silently operate in an unknown zone.
"""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Friendly region aliases mapped to IANA timezone keys. IANA keys are also
# accepted directly by ``zone_for``.
REGIONS: dict[str, str] = {
    "utc": "UTC",
    "new-york": "America/New_York",
    "los-angeles": "America/Los_Angeles",
    "sao-paulo": "America/Sao_Paulo",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "dubai": "Asia/Dubai",
    "kolkata": "Asia/Kolkata",
    "shanghai": "Asia/Shanghai",
    "singapore": "Asia/Singapore",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "auckland": "Pacific/Auckland",
}


class UnknownRegionError(ValueError):
    """Raised when a region name does not resolve to an IANA timezone."""


def zone_for(region: str) -> ZoneInfo:
    """Resolve a friendly region name or IANA key to a ``ZoneInfo``."""
    key = REGIONS.get(region.lower(), region)
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError as exc:
        known = ", ".join(sorted(REGIONS))
        raise UnknownRegionError(
            f"unknown region {region!r}; try one of: {known}"
        ) from exc


def require_aware(moment: datetime) -> datetime:
    """Return ``moment`` unchanged, or raise if it has no UTC offset.

    A naive datetime cannot be placed on the timeline, so conversion or
    formatting it would silently assume the host's local zone.
    """
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError(
            "datetime must be timezone-aware; attach a tzinfo/offset first"
        )
    return moment


def now_in(region: str) -> datetime:
    """Current timezone-aware time in the given region."""
    return datetime.now(zone_for(region))


def convert(moment: datetime, region: str) -> datetime:
    """Convert an aware datetime to the given region, preserving the instant."""
    require_aware(moment)
    return moment.astimezone(zone_for(region))


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 string, requiring an explicit offset or ``Z``."""
    return require_aware(datetime.fromisoformat(value))


def at_local_time(
    region: str,
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    *,
    fold: int = 0,
) -> datetime:
    """Build an aware datetime from a wall-clock time in a region.

    Around DST transitions a wall-clock time may be ambiguous (repeated) or
    nonexistent (skipped). ``fold`` picks the interpretation: for an
    ambiguous time ``0`` is the first/earlier occurrence and ``1`` the
    second; for a nonexistent time ``0`` uses the offset before the gap and
    ``1`` the offset after it. Use :func:`local_time_status` to detect these
    cases before scheduling anything.
    """
    return datetime(year, month, day, hour, minute, fold=fold, tzinfo=zone_for(region))


def local_time_status(
    region: str,
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
) -> str:
    """Classify a wall-clock time as ``unique``, ``ambiguous`` or ``nonexistent``."""
    zone = zone_for(region)
    base = datetime(year, month, day, hour, minute)
    first = base.replace(tzinfo=zone, fold=0)
    second = base.replace(tzinfo=zone, fold=1)
    if first.utcoffset() == second.utcoffset():
        return "unique"
    # Offsets differ, so this is a DST gap or overlap. In a gap the fold=0
    # offset maps to the later UTC instant; in an overlap to the earlier.
    if first.astimezone(UTC) > second.astimezone(UTC):
        return "nonexistent"
    return "ambiguous"
