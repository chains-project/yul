"""Core helpers built on the standard-library :mod:`zoneinfo` module.

All datetimes produced here are timezone-aware, so arithmetic and comparisons
stay correct across daylight-saving transitions.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = ZoneInfo("UTC")

REGIONS: dict[str, str] = {
    "utc": "UTC",
    "us-hawaii": "Pacific/Honolulu",
    "us-alaska": "America/Anchorage",
    "us-pacific": "America/Los_Angeles",
    "us-mountain": "America/Denver",
    "us-central": "America/Chicago",
    "us-eastern": "America/New_York",
    "brazil": "America/Sao_Paulo",
    "argentina": "America/Argentina/Buenos_Aires",
    "uk": "Europe/London",
    "central-europe": "Europe/Berlin",
    "eastern-europe": "Europe/Kyiv",
    "south-africa": "Africa/Johannesburg",
    "uae": "Asia/Dubai",
    "india": "Asia/Kolkata",
    "china": "Asia/Shanghai",
    "japan": "Asia/Tokyo",
    "singapore": "Asia/Singapore",
    "australia-east": "Australia/Sydney",
    "australia-west": "Australia/Perth",
    "new-zealand": "Pacific/Auckland",
}


def zone_for(region: str) -> ZoneInfo:
    """Return the IANA timezone for a named region.

    The lookup is case-insensitive and also accepts a raw IANA name such as
    ``"America/New_York"`` so callers are not limited to :data:`REGIONS`.
    """
    key = region.strip().lower()
    name = REGIONS.get(key, region.strip())
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        known = ", ".join(sorted(REGIONS))
        raise KeyError(
            f"unknown region {region!r}; known regions: {known}"
        ) from exc


def localize(naive: datetime, region: str) -> datetime:
    """Attach ``region``'s timezone to a naive datetime.

    ``fold`` is honoured, so a local time that occurs twice (the end of DST)
    resolves deterministically. Times that fall in a spring-forward gap are
    shifted forward by the size of the gap, matching common wall-clock
    expectations rather than silently keeping an invalid offset.
    """
    if naive.tzinfo is not None:
        raise ValueError(
            "localize() expects a naive datetime; "
            "use to_region() to convert an aware value"
        )
    zone = zone_for(region)
    localized = naive.replace(tzinfo=zone)
    # Detect a gap: round-tripping through UTC would land on a different
    # wall-clock time if the naive value does not exist in this zone.
    round_trip = localized.astimezone(UTC).astimezone(zone)
    if round_trip.replace(tzinfo=None) != naive:
        gap = round_trip - localized
        localized = (naive + gap).replace(tzinfo=zone)
    return localized


def now(region: str = "utc") -> datetime:
    """Current time in ``region`` as an aware datetime."""
    return datetime.now(zone_for(region))


def to_region(moment: datetime, region: str) -> datetime:
    """Convert ``moment`` into ``region``'s timezone.

    Naive datetimes are assumed to be UTC. The returned value is always
    timezone-aware.
    """
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(zone_for(region))


def table(region: str = "utc", at: datetime | None = None) -> list[dict[str, object]]:
    """Return each region with its local time and current UTC offset."""
    reference = at if at is not None else now(region)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=UTC)
    rows: list[dict[str, object]] = []
    for name in sorted(REGIONS):
        local = to_region(reference, name)
        offset = local.utcoffset() or timedelta()
        rows.append(
            {
                "region": name,
                "zone": REGIONS[name],
                "local_time": local.isoformat(),
                "utc_offset": _format_offset(offset),
                "dst": bool(local.dst()),
            }
        )
    return rows


def _format_offset(offset: timedelta) -> str:
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, remainder = divmod(total, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"
