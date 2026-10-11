from __future__ import annotations

import argparse
from datetime import datetime

from .core import convert, list_zones, now_in


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="worldtime",
        description="Timezone-aware datetime helper for world regions",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    now_parser = sub.add_parser("now", help="Show current time in one or more zones")
    now_parser.add_argument("zones", nargs="+", help="IANA names, e.g. America/New_York")

    convert_parser = sub.add_parser("convert", help="Convert an ISO-8601 datetime to a zone")
    convert_parser.add_argument("value", help="e.g. 2026-10-03T12:00:00+00:00")
    convert_parser.add_argument("zone", help="Target IANA timezone name")

    zones_parser = sub.add_parser("zones", help="List available timezone names")
    zones_parser.add_argument("--prefix", default=None, help="Filter, e.g. Europe/")

    args = parser.parse_args(argv)

    if args.command == "now":
        for name in args.zones:
            print(f"{name}: {now_in(name).isoformat()}")
        return 0

    if args.command == "convert":
        parsed = datetime.fromisoformat(args.value)
        print(convert(parsed, args.zone).isoformat())
        return 0

    if args.command == "zones":
        for name in list_zones(args.prefix):
            print(name)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
