"""Core helpers built on :mod:`zoneinfo` for timezone-aware datetimes."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def now_in(region: str) -> datetime:
    """Return the current time in the given IANA ``region``."""
    return datetime.now(ZoneInfo(region))


def ensure_aware(moment: datetime, assume: str = "UTC") -> datetime:
    """Return an aware datetime, assuming ``assume`` when ``moment`` is naive."""
    if moment.tzinfo is not None:
        return moment
    return moment.replace(tzinfo=ZoneInfo(assume))


def convert(moment: datetime, region: str) -> datetime:
    """Convert an aware ``moment`` to the given IANA ``region``."""
    if moment.tzinfo is None:
        raise ValueError("moment must be timezone-aware; use ensure_aware() first")
    return moment.astimezone(ZoneInfo(region))


def to_utc(moment: datetime) -> datetime:
    """Convert an aware ``moment`` to UTC."""
    return convert(moment, "UTC")


def offset_hours(moment: datetime, region: str) -> float:
    """Return the UTC offset of ``region`` at ``moment``, in hours."""
    offset = convert(moment, region).utcoffset()
    if offset is None:
        raise ValueError(f"{region} has no UTC offset at {moment!r}")
    return offset.total_seconds() / 3600
