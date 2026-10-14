from datetime import UTC, datetime
from zoneinfo import ZoneInfo, available_timezones


def now_in(zone: str) -> datetime:
    """Current time in the given IANA zone, e.g. 'Europe/Paris'."""
    return datetime.now(ZoneInfo(zone))


def ensure_aware(dt: datetime, zone: str) -> datetime:
    """Attach `zone` to a naive datetime; return aware datetimes unchanged.

    Ambiguous wall times (DST fall-back) resolve to the first occurrence (fold=0).
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo(zone))
    return dt


def to_utc(dt: datetime) -> datetime:
    """Convert an aware datetime to UTC. Naive datetimes are rejected."""
    if dt.tzinfo is None:
        raise ValueError("naive datetime; call ensure_aware() first")
    return dt.astimezone(UTC)


def convert(dt: datetime, zone: str) -> datetime:
    """Convert an aware datetime to another IANA zone."""
    if dt.tzinfo is None:
        raise ValueError("naive datetime; call ensure_aware() first")
    return dt.astimezone(ZoneInfo(zone))


def list_zones() -> list[str]:
    return sorted(available_timezones())
