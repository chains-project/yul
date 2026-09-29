from __future__ import annotations

import argparse
from collections.abc import Sequence

from .timezones import available_regions, convert, parse, world_clock

DEFAULT_ZONES = (
    "UTC",
    "America/New_York",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Paris",
    "Africa/Nairobi",
    "Asia/Dubai",
    "Asia/Kolkata",
    "Asia/Shanghai",
    "Asia/Tokyo",
    "Australia/Sydney",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldclock",
        description="Show and convert timezone-aware datetimes across the world.",
    )
    subparsers = parser.add_subparsers(dest="command")

    now_parser = subparsers.add_parser("now", help="show the current time in zones")
    now_parser.add_argument(
        "-z",
        "--zone",
        action="append",
        dest="zones",
        metavar="ZONE",
        help="IANA time zone (repeatable); defaults to a set of major regions",
    )

    convert_parser = subparsers.add_parser("convert", help="convert an ISO 8601 datetime")
    convert_parser.add_argument("value", help="ISO 8601 datetime, e.g. 2024-03-10T07:00:00Z")
    convert_parser.add_argument("-z", "--zone", required=True, dest="zone", metavar="ZONE")
    convert_parser.add_argument(
        "--from",
        dest="source",
        default="UTC",
        metavar="ZONE",
        help="zone to assume when the input has no offset (default: UTC)",
    )

    list_parser = subparsers.add_parser("list", help="list available IANA regions")
    list_parser.add_argument("prefix", nargs="?", help="filter by region, e.g. Asia")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for name in available_regions(args.prefix):
            print(name)
        return 0

    if args.command == "convert":
        moment = parse(args.value, args.source)
        print(convert(moment, args.zone).isoformat())
        return 0

    zones = getattr(args, "zones", None) or DEFAULT_ZONES
    for zone, moment in world_clock(zones).items():
        print(f"{zone:<28} {moment.isoformat()}")
    return 0
