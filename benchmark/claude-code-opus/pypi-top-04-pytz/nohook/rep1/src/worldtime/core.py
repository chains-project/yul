"""Core timezone helpers built on the standard library's zoneinfo.

Convention: store and compare datetimes in UTC; convert to a local zone only for display
or when interpreting user-supplied wall-clock times.
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo


def now_in(tz: str) -> datetime:
    """Current time in the given IANA zone, e.g. "Asia/Tokyo"."""
    return datetime.now(ZoneInfo(tz))


def localize(naive: datetime, tz: str, *, fold: int = 0) -> datetime:
    """Attach a zone to a naive wall-clock time.

    `fold` resolves ambiguous times during a DST fall-back: 0 = first occurrence,
    1 = second. Nonexistent times (spring-forward gap) are not rejected by zoneinfo;
    use `is_valid_local` to check.
    """
    if naive.tzinfo is not None:
        raise ValueError("expected a naive datetime")
    return naive.replace(tzinfo=ZoneInfo(tz), fold=fold)


def is_valid_local(dt: datetime) -> bool:
    """False if an aware datetime's wall time falls in a DST gap (doesn't exist)."""
    roundtrip = dt.astimezone(UTC).astimezone(dt.tzinfo)
    return roundtrip.replace(tzinfo=None) == dt.replace(tzinfo=None)


def ensure_aware(dt: datetime) -> datetime:
    """Raise if `dt` is naive; guards boundaries where naive values must not leak in."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"naive datetime not allowed: {dt!r}")
    return dt


def to_utc(dt: datetime) -> datetime:
    return ensure_aware(dt).astimezone(UTC)


def convert(dt: datetime, tz: str) -> datetime:
    """Convert an aware datetime to another IANA zone."""
    return ensure_aware(dt).astimezone(ZoneInfo(tz))
