"""Core timezone-aware datetime helpers.

All datetimes returned by this module are aware (carry a ``tzinfo``).
Convert on ingest, keep UTC internally, convert for display.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = timezone.utc
ZoneLike = str | ZoneInfo


class UnknownTimezoneError(ValueError):
    """Raised when an IANA timezone name cannot be resolved."""


class NaiveDatetimeError(ValueError):
    """Raised when a naive datetime is passed where an aware one is required."""


class AmbiguousTimeError(ValueError):
    """Raised for a wall-clock time that occurs twice (DST fall-back)."""


class NonExistentTimeError(ValueError):
    """Raised for a wall-clock time that never occurs (DST spring-forward)."""


def get_zone(zone: ZoneLike) -> ZoneInfo:
    """Resolve a timezone name or pass through an existing ``ZoneInfo``."""
    if isinstance(zone, ZoneInfo):
        return zone
    try:
        return ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise UnknownTimezoneError(f"Unknown IANA timezone: {zone!r}") from exc


def ensure_aware(dt: datetime) -> datetime:
    """Return ``dt`` unchanged if aware, otherwise raise."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveDatetimeError(
            "Naive datetime; attach a tzinfo (e.g. datetime.now(timezone.utc)) first"
        )
    return dt


def now(zone: ZoneLike = UTC) -> datetime:
    """Current instant, expressed in ``zone``."""
    return datetime.now(get_zone(zone))


def to_utc(dt: datetime) -> datetime:
    """Convert any aware datetime to UTC."""
    return ensure_aware(dt).astimezone(UTC)


def to_zone(dt: datetime, zone: ZoneLike) -> datetime:
    """Convert any aware datetime to ``zone``."""
    return ensure_aware(dt).astimezone(get_zone(zone))


def localize(wall: datetime, zone: ZoneLike, *, fold: int | None = None) -> datetime:
    """Attach ``zone`` to a naive wall-clock time.

    Raises :class:`NonExistentTimeError` for skipped times and
    :class:`AmbiguousTimeError` for repeated times unless ``fold`` is given.
    """
    z = get_zone(zone)
    if wall.tzinfo is not None:
        raise ValueError("localize() expects a naive wall-clock datetime")
    candidate = wall.replace(tzinfo=z)
    round_trip = candidate.astimezone(UTC).astimezone(z)
    if round_trip.replace(tzinfo=None) != wall:
        raise NonExistentTimeError(f"{wall} does not exist in {z.key}")
    if candidate.utcoffset() != wall.replace(tzinfo=z, fold=1).utcoffset() and fold is None:
        raise AmbiguousTimeError(f"{wall} is ambiguous in {z.key}; pass fold=0 or fold=1")
    if fold is not None:
        candidate = wall.replace(tzinfo=z, fold=fold)
    return candidate


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 string, requiring an explicit offset."""
    dt = datetime.fromisoformat(value)
    return ensure_aware(dt)


def to_iso(dt: datetime) -> str:
    """Serialize an aware datetime to ISO-8601 with offset."""
    return ensure_aware(dt).isoformat()


def world_clock(
    instant: datetime | None = None,
    regions: dict[str, ZoneLike] | None = None,
) -> dict[str, datetime]:
    """Snapshot ``instant`` (default: now) across named regions."""
    if regions is None:
        regions = DEFAULT_REGIONS
    moment = to_utc(instant) if instant is not None else now(UTC)
    return {name: to_zone(moment, zone) for name, zone in regions.items()}


DEFAULT_REGIONS: dict[str, str] = {
    "Honolulu": "Pacific/Honolulu",
    "Los Angeles": "America/Los_Angeles",
    "New York": "America/New_York",
    "London": "Europe/London",
    "Berlin": "Europe/Berlin",
    "Dubai": "Asia/Dubai",
    "Kolkata": "Asia/Kolkata",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
    "Auckland": "Pacific/Auckland",
}
