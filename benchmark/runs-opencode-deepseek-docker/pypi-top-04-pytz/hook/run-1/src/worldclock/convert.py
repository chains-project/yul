"""Timezone-aware datetime conversion helpers built on :mod:`zoneinfo`.

Compatible with Python 3.9+ (the versions of ``zoneinfo`` bundled with
CPython 3.9 through 3.11 handle the IANA database identically for the
operations used here).  On platforms that do not ship an IANA database
(notably Windows), install the ``tzdata`` package.
"""

from __future__ import annotations

from datetime import datetime, timezone, tzinfo
from typing import Dict, Iterable, List, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

__all__ = [
    "UnknownTimeZoneError",
    "get_zone",
    "available_zones",
    "now_in",
    "parse_iso",
    "localize",
    "convert",
    "to_utc",
    "local_times",
    "is_ambiguous",
    "is_nonexistent",
]

ZoneLike = Union[str, tzinfo]


class UnknownTimeZoneError(ValueError):
    """Raised when a timezone name is absent from the IANA database."""


def get_zone(zone: ZoneLike) -> tzinfo:
    """Return a :class:`~datetime.tzinfo` for *zone*.

    Strings are resolved against the IANA database using
    :class:`zoneinfo.ZoneInfo`.  An existing :class:`tzinfo` instance is
    returned unchanged, which lets callers mix names and objects freely.
    """
    if isinstance(zone, tzinfo):
        return zone
    try:
        return ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise UnknownTimeZoneError(zone) from exc


def available_zones() -> List[str]:
    """Return every IANA timezone name, sorted for stable output."""
    return sorted(available_timezones())


def now_in(zone: ZoneLike) -> datetime:
    """Return the current time as an aware datetime in *zone*."""
    return datetime.now(get_zone(zone))


def parse_iso(text: str, *, assume: ZoneLike = "UTC") -> datetime:
    """Parse an ISO-8601 timestamp into an aware datetime.

    A leading/trailing ``Z`` is accepted as UTC.  When *text* carries no
    offset it is interpreted as wall-clock time in *assume*.
    """
    cleaned = text.strip()
    if cleaned.endswith(("Z", "z")):
        cleaned = cleaned[:-1] + "+00:00"
    parsed = datetime.fromisoformat(cleaned)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=get_zone(assume))
    return parsed


def localize(naive: datetime, zone: ZoneLike, *, fold: int = 0) -> datetime:
    """Attach *zone* to a naive datetime.

    For ambiguous wall-clock times produced by a DST fall-back, ``fold=0``
    selects the first (usually daylight) occurrence and ``fold=1`` the
    second (usually standard) one.
    """
    if naive.tzinfo is not None:
        raise ValueError("localize() expects a naive datetime")
    if fold not in (0, 1):
        raise ValueError("fold must be 0 or 1")
    return naive.replace(tzinfo=get_zone(zone), fold=fold)


def convert(value: datetime, target: ZoneLike, *, source: ZoneLike = None) -> datetime:
    """Convert *value* to the *target* timezone.

    Aware datetimes keep their instant.  Naive datetimes are first
    interpreted in *source*, which is therefore required for them.
    """
    if value.tzinfo is None:
        if source is None:
            raise ValueError(
                "a naive datetime needs an explicit source timezone"
            )
        value = localize(value, source)
    return value.astimezone(get_zone(target))


def to_utc(value: datetime, *, source: ZoneLike = None) -> datetime:
    """Convert *value* to UTC."""
    return convert(value, timezone.utc, source=source)


def local_times(
    value: datetime,
    zones: Iterable[ZoneLike],
    *,
    source: ZoneLike = None,
) -> Dict[str, datetime]:
    """Show the same instant as it reads in each of *zones*.

    Returns a mapping of IANA name to aware datetime.  The instant is
    never changed, only its representation.
    """
    result: Dict[str, datetime] = {}
    for zone in zones:
        resolved = get_zone(zone)
        key = getattr(resolved, "key", str(resolved))
        result[key] = convert(value, resolved, source=source)
    return result


def is_ambiguous(naive: datetime, zone: ZoneLike) -> bool:
    """True if *naive* occurs twice in *zone* (DST fall-back overlap)."""
    resolved = get_zone(zone)
    first = naive.replace(tzinfo=resolved, fold=0).utcoffset()
    second = naive.replace(tzinfo=resolved, fold=1).utcoffset()
    return first != second


def is_nonexistent(naive: datetime, zone: ZoneLike) -> bool:
    """True if *naive* is skipped in *zone* (DST spring-forward gap)."""
    resolved = get_zone(zone)
    localized = naive.replace(tzinfo=resolved)
    round_tripped = localized.astimezone(timezone.utc).astimezone(resolved)
    return round_tripped.replace(tzinfo=None) != naive
