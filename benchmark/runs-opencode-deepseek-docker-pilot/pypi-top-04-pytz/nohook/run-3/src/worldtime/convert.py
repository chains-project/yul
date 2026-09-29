"""Timezone-aware conversion helpers built on the standard library ``zoneinfo``."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc

ZoneLike = str | ZoneInfo


def resolve_zone(zone: ZoneLike) -> ZoneInfo:
    """Return a :class:`ZoneInfo` for an IANA name such as ``America/New_York``.

    Passing an existing ``ZoneInfo`` is allowed and returned unchanged.
    """
    if isinstance(zone, ZoneInfo):
        return zone
    try:
        return ZoneInfo(zone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown timezone: {zone!r}") from exc


def now_in(zone: ZoneLike) -> datetime:
    """Current time in ``zone`` as a timezone-aware datetime."""
    return datetime.now(resolve_zone(zone))


def to_zone(moment: datetime, zone: ZoneLike) -> datetime:
    """Convert an aware datetime to another timezone.

    Naive datetimes are rejected: an unqualified wall-clock time is ambiguous,
    so it must be anchored to a timezone before conversion.
    """
    if moment.tzinfo is None:
        raise ValueError("cannot convert a naive datetime; attach a timezone first")
    return moment.astimezone(resolve_zone(zone))


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 string into an aware datetime.

    A value without an offset is treated as UTC so downstream conversions are
    always well defined.
    """
    moment = datetime.fromisoformat(value)
    if moment.tzinfo is None:
        return moment.replace(tzinfo=UTC)
    return moment


def convert_iso(value: str, zone: ZoneLike) -> datetime:
    """Parse an ISO-8601 string and convert it into ``zone``."""
    return to_zone(parse_iso(value), zone)


def convert_all(moment: datetime, zones: Iterable[str]) -> dict[str, datetime]:
    """Convert ``moment`` into each zone, returning a mapping of name to time."""
    return {name: to_zone(moment, name) for name in zones}
