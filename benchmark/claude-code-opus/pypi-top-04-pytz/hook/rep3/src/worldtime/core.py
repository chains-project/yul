"""Core helpers built on the standard-library ``zoneinfo`` module.

Rules followed throughout:
- Never produce or accept naive datetimes silently.
- Store/compare in UTC; convert to local zones only for display.
- Use IANA zone names (e.g. "America/New_York"), not abbreviations like "EST".
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc


class NaiveDatetimeError(ValueError):
    """Raised when a naive datetime is passed where an aware one is required."""


@lru_cache(maxsize=None)
def get_zone(name: str) -> ZoneInfo:
    """Return the ZoneInfo for an IANA name, with a clear error if unknown."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown IANA time zone: {name!r}") from exc


def ensure_aware(dt: datetime) -> datetime:
    """Return ``dt`` unchanged if aware; raise if it is naive."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveDatetimeError(f"Naive datetime not allowed: {dt!r}")
    return dt


def now_in(zone: str) -> datetime:
    """Current time in the given zone."""
    return datetime.now(get_zone(zone))


def to_utc(dt: datetime) -> datetime:
    """Convert an aware datetime to UTC."""
    return ensure_aware(dt).astimezone(UTC)


def convert(dt: datetime, zone: str) -> datetime:
    """Convert an aware datetime to another zone."""
    return ensure_aware(dt).astimezone(get_zone(zone))


def localize(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, *, zone: str, fold: int = 0
) -> datetime:
    """Build an aware datetime from wall-clock time in ``zone``.

    ``fold`` disambiguates repeated times at DST fall-back
    (0 = first occurrence, 1 = second). See PEP 495.
    """
    return datetime(year, month, day, hour, minute, tzinfo=get_zone(zone), fold=fold)
