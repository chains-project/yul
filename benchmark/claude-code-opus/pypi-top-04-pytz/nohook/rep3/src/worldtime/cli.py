"""Command-line entry point: show one instant across several timezones."""

from __future__ import annotations

import argparse
from datetime import datetime

from worldtime.core import localize, now_utc, world_clock

DEFAULT_ZONES = [
    "America/Los_Angeles",
    "America/New_York",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Berlin",
    "Africa/Lagos",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Australia/Sydney",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "zones", nargs="*", default=DEFAULT_ZONES, help="IANA zone names (default: a world sample)"
    )
    parser.add_argument(
        "--at",
        help="ISO 8601 time to convert instead of now. If it has no offset, it's read in --from-zone.",
    )
    parser.add_argument("--from-zone", default="UTC", help="zone for a naive --at value (default: UTC)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.at:
        moment = datetime.fromisoformat(args.at)
        if moment.tzinfo is None:
            moment = localize(moment, args.from_zone)
    else:
        moment = now_utc()

    for zone, local in world_clock(moment, args.zones).items():
        print(f"{zone:<22} {local:%Y-%m-%d %H:%M %Z (UTC%z)}")
