"""Command-line entry point: show one instant across several world regions."""

from __future__ import annotations

import argparse
import sys

from worldclock.timezones import format_iso, now, parse_iso, to_zone

DEFAULT_ZONES = (
    "UTC",
    "America/Los_Angeles",
    "America/New_York",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Australia/Sydney",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldclock",
        description="Show a single instant across world regions.",
    )
    parser.add_argument(
        "zones",
        nargs="*",
        help="IANA timezone names (default: a sample of world regions)",
    )
    parser.add_argument(
        "-a",
        "--at",
        metavar="ISO8601",
        help="timezone-aware instant to display instead of the current time",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    zones = list(args.zones) or list(DEFAULT_ZONES)

    try:
        instant = parse_iso(args.at) if args.at else now("UTC")
        rows = [(zone, to_zone(instant, zone)) for zone in zones]
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
        return 2

    width = max(len(zone) for zone, _ in rows)
    for zone, local in rows:
        print(f"{zone:<{width}}  {format_iso(local)}  ({local.tzname()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
