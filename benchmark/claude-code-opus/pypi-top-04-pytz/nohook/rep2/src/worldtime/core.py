"""Core helpers built on the standard-library ``zoneinfo`` module.

Conventions:
- Store and compute in UTC; convert to local zones only for display/input.
- Never use naive datetimes for real moments in time. ``ensure_aware``
  rejects them so bugs surface early instead of silently using local time.
- Zones are IANA names (e.g. "America/New_York"), never abbreviations like
  "EST", which are ambiguous and don't track daylight saving time.
"""

from __future__ import annotations

from datetime import UTC, datetime
from functools import cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = ["UTC", "convert", "ensure_aware", "get_zone", "localize", "now_in", "now_utc"]


@cache
def get_zone(name: str) -> ZoneInfo:
    """Return the ZoneInfo for an IANA zone name, with a clear error if unknown."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown IANA time zone: {name!r}") from exc


def now_utc() -> datetime:
    """Current time as an aware UTC datetime."""
    return datetime.now(UTC)


def now_in(zone: str) -> datetime:
    """Current time as an aware datetime in the given zone."""
    return datetime.now(get_zone(zone))


def ensure_aware(dt: datetime) -> datetime:
    """Raise if ``dt`` is naive; return it unchanged otherwise."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"Expected a timezone-aware datetime, got naive {dt!r}")
    return dt


def localize(naive: datetime, zone: str, *, fold: int = 0) -> datetime:
    """Attach a zone to a naive wall-clock time.

    During a DST "fall back" the same wall time occurs twice; ``fold=0``
    picks the first occurrence and ``fold=1`` the second. Wall times that
    don't exist (skipped by "spring forward") raise ``ValueError``.
    """
    if naive.tzinfo is not None:
        raise ValueError("localize() expects a naive datetime; use convert() instead")
    tz = get_zone(zone)
    dt = naive.replace(tzinfo=tz, fold=fold)
    # A nonexistent wall time doesn't survive a round trip through UTC.
    if dt.astimezone(UTC).astimezone(tz).replace(tzinfo=None) != naive:
        raise ValueError(f"{naive.isoformat()} does not exist in {zone} (DST gap)")
    return dt


def convert(dt: datetime, zone: str) -> datetime:
    """Convert an aware datetime to another zone (same instant, new wall time)."""
    return ensure_aware(dt).astimezone(get_zone(zone))
