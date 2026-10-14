from datetime import UTC, datetime
from functools import cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@cache
def get_zone(name: str) -> ZoneInfo:
    """Return the ZoneInfo for an IANA name like 'Europe/Berlin'."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown timezone: {name!r}") from exc


def ensure_aware(dt: datetime) -> datetime:
    """Reject naive datetimes so they can't be silently misinterpreted."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"Expected a timezone-aware datetime, got naive {dt!r}")
    return dt


def now_in(zone: str) -> datetime:
    return datetime.now(get_zone(zone))


def to_utc(dt: datetime) -> datetime:
    return ensure_aware(dt).astimezone(UTC)


def convert(dt: datetime, zone: str) -> datetime:
    return ensure_aware(dt).astimezone(get_zone(zone))
