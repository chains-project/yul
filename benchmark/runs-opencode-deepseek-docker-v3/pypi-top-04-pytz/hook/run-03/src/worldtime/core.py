from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones

UTC = timezone.utc


def get_zone(name: str) -> ZoneInfo:
    return ZoneInfo(name)


def list_zones(prefix: str | None = None) -> list[str]:
    zones = available_timezones()
    if prefix:
        zones = {zone for zone in zones if zone.startswith(prefix)}
    return sorted(zones)


def now_in(name: str) -> datetime:
    return datetime.now(get_zone(name))


def ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return dt


def convert(dt: datetime, name: str) -> datetime:
    return ensure_aware(dt).astimezone(get_zone(name))


def to_utc(dt: datetime) -> datetime:
    return ensure_aware(dt).astimezone(UTC)
