"""Core helpers for timezone-aware datetime handling.

All public functions return *aware* :class:`~datetime.datetime` objects. IANA
timezone identifiers (e.g. ``"America/New_York"``) are used throughout, so
daylight-saving transitions, historical offsets and half-hour/45-minute
offsets are handled correctly by :mod:`zoneinfo`.
"""

from __future__ import annotations

from datetime import datetime, timezone, tzinfo
from typing import Dict, Optional, Union

try:
    from zoneinfo import ZoneInfo, available_timezones
except ImportError as exc:  # pragma: no cover - Python < 3.9
    raise ImportError(
        "worldtime requires Python 3.9+ for the standard-library zoneinfo module"
    ) from exc

UTC = ZoneInfo("UTC")

TimezoneLike = Union[str, tzinfo]

# A few representative IANA zones for common regions of the world.
REGIONS: Dict[str, str] = {
    "utc": "UTC",
    "us-east": "America/New_York",
    "us-central": "America/Chicago",
    "us-mountain": "America/Denver",
    "us-west": "America/Los_Angeles",
    "brazil": "America/Sao_Paulo",
    "uk": "Europe/London",
    "central-europe": "Europe/Berlin",
    "eastern-europe": "Europe/Kyiv",
    "india": "Asia/Kolkata",
    "china": "Asia/Shanghai",
    "japan": "Asia/Tokyo",
    "australia-east": "Australia/Sydney",
    "new-zealand": "Pacific/Auckland",
}


def to_zone(zone: TimezoneLike) -> tzinfo:
    """Resolve ``zone`` to a :class:`tzinfo` instance.

    Accepts an IANA name, a :class:`ZoneInfo`, or any other ``tzinfo`` (e.g.
    the fixed-offset objects produced by :func:`datetime.fromisoformat`).
    Raises :class:`ZoneInfoNotFoundError` for unknown names.
    """
    if isinstance(zone, tzinfo):
        return zone
    return ZoneInfo(zone)


def _zone_name(zone: TimezoneLike) -> str:
    return zone if isinstance(zone, str) else getattr(zone, "key", str(zone))


def current_time(zone: TimezoneLike = UTC) -> datetime:
    """Return the current time in ``zone`` as an aware datetime."""
    return datetime.now(tz=to_zone(zone))


def region_time(region: str, at: Optional[datetime] = None) -> datetime:
    """Return the time in a named region.

    ``region`` is a key from :data:`REGIONS` (case-insensitive). When ``at`` is
    given it must be timezone-aware and is converted; otherwise the current
    time is returned.
    """
    key = region.strip().lower()
    try:
        zone = REGIONS[key]
    except KeyError:
        known = ", ".join(sorted(REGIONS))
        raise KeyError(f"unknown region {region!r}; known regions: {known}") from None
    if at is None:
        return current_time(zone)
    return convert(at, zone)


def convert(dt: datetime, zone: TimezoneLike) -> datetime:
    """Convert an aware datetime to ``zone``.

    The instant in time is preserved; only the wall-clock representation
    changes. Naive datetimes are rejected to avoid silent, incorrect results.
    """
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("convert() requires a timezone-aware datetime")
    return dt.astimezone(to_zone(zone))


def localize(
    dt: datetime,
    zone: TimezoneLike,
    *,
    fold: int = 0,
    strict: bool = False,
) -> datetime:
    """Attach ``zone`` to a naive datetime, returning an aware datetime.

    ``fold`` selects the offset to use during an ambiguous hour (the repeated
    hour when clocks fall back): ``0`` for the first occurrence, ``1`` for the
    second. When ``strict`` is true, a naive time that is either ambiguous or
    falls in a daylight-saving gap raises :class:`ValueError`.
    """
    if dt.tzinfo is not None and dt.utcoffset() is not None:
        raise ValueError("localize() requires a naive datetime")
    tz = to_zone(zone)
    aware = dt.replace(tzinfo=tz, fold=fold)

    if strict:
        if is_ambiguous(dt, tz):
            raise ValueError(f"{dt!r} is ambiguous in {_zone_name(zone)}")
        if is_nonexistent(dt, tz):
            raise ValueError(
                f"{dt!r} does not exist in {_zone_name(zone)} "
                "(skipped by a daylight-saving transition)"
            )
    return aware


def parse(
    value: str,
    zone: Optional[TimezoneLike] = None,
    *,
    strict: bool = False,
) -> datetime:
    """Parse an ISO 8601 string into an aware datetime.

    A trailing ``Z`` and explicit numeric offsets are understood. If the string
    carries no offset, ``zone`` is applied (defaulting to UTC). ``strict`` is
    forwarded to :func:`localize` for offset-less input.
    """
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"

    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is not None and parsed.utcoffset() is not None:
        target = zone if zone is not None else parsed.tzinfo
        return convert(parsed, target)
    return localize(parsed, zone if zone is not None else UTC, strict=strict)


def is_ambiguous(dt: datetime, zone: TimezoneLike) -> bool:
    """Return ``True`` if naive ``dt`` occurs twice in ``zone`` (DST fall-back).

    The input is treated as wall-clock time in ``zone`` regardless of any
    ``tzinfo`` it carries.
    """
    tz = to_zone(zone)
    naive = dt.replace(tzinfo=None)
    first = naive.replace(tzinfo=tz, fold=0)
    second = naive.replace(tzinfo=tz, fold=1)
    if first.utcoffset() == second.utcoffset():
        return False
    return not is_nonexistent(naive, tz)


def is_nonexistent(dt: datetime, zone: TimezoneLike) -> bool:
    """Return ``True`` if naive ``dt`` is skipped by a DST spring-forward."""
    tz = to_zone(zone)
    naive = dt.replace(tzinfo=None)
    aware = naive.replace(tzinfo=tz)
    return aware.astimezone(UTC).astimezone(tz).replace(tzinfo=None) != naive


def available_regions() -> Dict[str, str]:
    """Return a copy of the built-in region-to-timezone mapping."""
    return dict(REGIONS)


def known_zones() -> frozenset:
    """Return the set of all IANA timezone names known to the platform."""
    return available_timezones()
