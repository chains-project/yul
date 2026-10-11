"""Timezone-aware datetime helpers for working across world regions."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "DEFAULT_ZONES",
    "ensure_aware",
    "format_in_zone",
    "get_zone",
    "local_time_in_zones",
    "now_in",
    "to_zone",
]

DEFAULT_ZONES = (
    "UTC",
    "America/New_York",
    "Europe/London",
    "Asia/Tokyo",
    "Australia/Sydney",
)


def get_zone(name: str) -> ZoneInfo:
    """Return a ``ZoneInfo`` for an IANA name such as ``America/New_York``."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown timezone: {name!r}") from exc


def ensure_aware(dt: datetime, assume: str = "UTC") -> datetime:
    """Return an aware datetime, interpreting naive input in ``assume``."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=get_zone(assume))
    return dt


def now_in(name: str) -> datetime:
    """Return the current timezone-aware datetime in the given region."""
    return datetime.now(get_zone(name))


def to_zone(dt: datetime, name: str) -> datetime:
    """Convert an aware (or naive) datetime to the given timezone."""
    return ensure_aware(dt).astimezone(get_zone(name))


def format_in_zone(
    dt: datetime,
    name: str,
    fmt: str = "%Y-%m-%d %H:%M:%S %Z%z",
) -> str:
    """Format a datetime in the target zone, including its UTC offset."""
    return to_zone(dt, name).strftime(fmt)


def local_time_in_zones(
    names: Iterable[str] = DEFAULT_ZONES,
    when: datetime | None = None,
) -> dict[str, datetime]:
    """Map region names to the same instant expressed in each zone."""
    moment = datetime.now(timezone.utc) if when is None else ensure_aware(when)
    return {name: to_zone(moment, name) for name in names}
