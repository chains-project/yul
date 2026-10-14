"""Command-line entry point: show the current time (or a given time) across zones."""

from __future__ import annotations

import argparse
from datetime import datetime

from worldtime.core import convert, ensure_aware, now_utc

DEFAULT_ZONES = [
    "UTC",
    "America/Los_Angeles",
    "America/New_York",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Berlin",
    "Africa/Lagos",
    "Asia/Kolkata",
    "Asia/Shanghai",
    "Asia/Tokyo",
    "Australia/Sydney",
    "Pacific/Auckland",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zones", nargs="*", help="IANA zone names (default: a world sample)")
    parser.add_argument(
        "--at",
        help="ISO 8601 time with offset, e.g. 2026-03-29T01:30:00+00:00 (default: now)",
    )
    args = parser.parse_args(argv)

    try:
        moment = ensure_aware(datetime.fromisoformat(args.at)) if args.at else now_utc()
        rows = [(zone, convert(moment, zone)) for zone in args.zones or DEFAULT_ZONES]
    except ValueError as exc:
        parser.error(str(exc))

    width = max(len(zone) for zone, _ in rows)
    for zone, local in rows:
        print(f"{zone:<{width}}  {local:%Y-%m-%d %H:%M %Z (UTC%z)}")
    return 0
