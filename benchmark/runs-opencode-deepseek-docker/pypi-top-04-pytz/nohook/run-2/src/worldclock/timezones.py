from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

__all__ = [
    "UTC",
    "UnknownTimeZoneError",
    "available_regions",
    "convert",
    "get_zone",
    "localize",
    "now",
    "parse",
    "to_utc",
    "world_clock",
]


class UnknownTimeZoneError(ValueError):
    def __init__(self, key: object) -> None:
        super().__init__(f"unknown time zone: {key!r}")
        self.key = key


def get_zone(key: str | ZoneInfo) -> ZoneInfo:
    if isinstance(key, ZoneInfo):
        return key
    try:
        return ZoneInfo(key)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise UnknownTimeZoneError(key) from exc


def now(tz: str | ZoneInfo = UTC) -> datetime:
    return datetime.now(get_zone(tz))


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("cannot convert a naive datetime; localize it first")
    return dt.astimezone(UTC)


def localize(dt: datetime, tz: str | ZoneInfo) -> datetime:
    zone = get_zone(tz)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=zone)
    return dt.astimezone(zone)


def convert(dt: datetime, tz: str | ZoneInfo) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("cannot convert a naive datetime; localize it first")
    return dt.astimezone(get_zone(tz))


def parse(text: str, tz: str | ZoneInfo = UTC) -> datetime:
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=get_zone(tz))
    return dt


def world_clock(
    zones: Iterable[str | ZoneInfo],
    at: datetime | None = None,
) -> Mapping[str, datetime]:
    reference = at if at is not None else datetime.now(UTC)
    if reference.tzinfo is None:
        raise ValueError("cannot use a naive reference datetime; localize it first")
    clock: dict[str, datetime] = {}
    for zone in zones:
        resolved = get_zone(zone)
        clock[str(resolved)] = reference.astimezone(resolved)
    return clock


def available_regions(prefix: str | None = None) -> list[str]:
    names = available_timezones()
    if prefix:
        names = {name for name in names if name.startswith(prefix)}
    return sorted(names)
