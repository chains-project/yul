"""Timezone-aware datetime helpers built on the stdlib ``zoneinfo`` module.

Conventions:
- Every datetime that enters or leaves this module is timezone-aware.
- Store and compute in UTC; convert to a local zone only for display/input.
- Zones are IANA names ("Europe/Berlin"), never abbreviations ("CET")
  or fixed offsets, so DST rules are applied correctly.
"""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones


class NaiveDatetimeError(ValueError):
    """Raised when a naive datetime is passed where an aware one is required."""


def get_zone(name: str) -> ZoneInfo:
    """Return the ZoneInfo for an IANA name, with a clear error if it's unknown."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown IANA timezone: {name!r}") from exc


def ensure_aware(dt: datetime) -> datetime:
    """Reject naive datetimes instead of silently guessing their zone."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveDatetimeError(f"Expected a timezone-aware datetime, got naive {dt!r}")
    return dt


def now_utc() -> datetime:
    """Current time as an aware UTC datetime (use instead of datetime.utcnow())."""
    return datetime.now(UTC)


def to_utc(dt: datetime) -> datetime:
    return ensure_aware(dt).astimezone(UTC)


def to_zone(dt: datetime, zone: str) -> datetime:
    return ensure_aware(dt).astimezone(get_zone(zone))


def localize(naive: datetime, zone: str, *, fold: int = 0) -> datetime:
    """Attach a zone to a naive wall-clock time (e.g. user input).

    ``fold`` picks which occurrence to use for ambiguous times during a DST
    fall-back (0 = first, 1 = second). Wall-clock times that don't exist
    (skipped during spring-forward) raise ValueError.
    """
    if naive.tzinfo is not None:
        raise ValueError("localize() expects a naive datetime; use to_zone() instead")
    aware = naive.replace(tzinfo=get_zone(zone), fold=fold)
    # A nonexistent local time won't survive a round trip through UTC.
    roundtrip = aware.astimezone(UTC).astimezone(aware.tzinfo)
    if roundtrip.replace(tzinfo=None) != naive:
        raise ValueError(f"{naive} does not exist in {zone} (skipped by a DST transition)")
    return aware


def is_ambiguous(naive: datetime, zone: str) -> bool:
    """True if the wall-clock time occurs twice in ``zone`` (DST fall-back)."""
    tz = get_zone(zone)
    return (
        naive.replace(tzinfo=tz, fold=0).utcoffset()
        != naive.replace(tzinfo=tz, fold=1).utcoffset()
    )


def world_clock(dt: datetime, zones: list[str]) -> dict[str, datetime]:
    """Return the same instant expressed in each of ``zones``."""
    return {zone: to_zone(dt, zone) for zone in zones}


def all_zone_names() -> list[str]:
    return sorted(available_timezones())
