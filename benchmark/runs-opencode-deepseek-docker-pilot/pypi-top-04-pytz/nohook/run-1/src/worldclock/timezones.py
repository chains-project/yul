"""Core utilities built on the standard-library :mod:`zoneinfo` module.

Every function returns or requires an aware :class:`~datetime.datetime`; naive
datetimes are rejected so that an instant is never ambiguous across regions.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones


def _as_zone(tz: str | ZoneInfo) -> ZoneInfo:
    """Return a :class:`ZoneInfo` for an IANA name or pass one through unchanged."""
    if isinstance(tz, ZoneInfo):
        return tz
    return ZoneInfo(tz)


def _require_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return dt


def now(tz: str | ZoneInfo) -> datetime:
    """Return the current instant as an aware datetime in the given zone."""
    return datetime.now(_as_zone(tz))


def to_zone(dt: datetime, tz: str | ZoneInfo) -> datetime:
    """Convert an aware datetime to another zone, preserving the instant."""
    return _require_aware(dt).astimezone(_as_zone(tz))


def parse_iso(value: str) -> datetime:
    """Parse an ISO 8601 string into an aware datetime, accepting a ``Z`` suffix."""
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    return _require_aware(datetime.fromisoformat(text))


def format_iso(dt: datetime) -> str:
    """Serialise an aware datetime to an ISO 8601 string with its UTC offset."""
    return _require_aware(dt).isoformat()


def list_zones(prefix: str | None = None) -> list[str]:
    """List known IANA zone names, optionally filtered by a name prefix."""
    zones = sorted(available_timezones())
    if prefix is not None:
        zones = [zone for zone in zones if zone.startswith(prefix)]
    return zones
