"""Command line interface for the worldtime package."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from worldtime.core import REGIONS, local_times, now, parse_datetime
from zoneinfo import ZoneInfoNotFoundError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldtime",
        description="Show the current time, or convert a datetime, across world regions.",
    )
    parser.add_argument(
        "regions",
        nargs="*",
        help="Region keys or IANA names (default: all known regions).",
    )
    parser.add_argument(
        "--at",
        metavar="DATETIME",
        help="ISO-8601 instant to convert instead of the current time.",
    )
    parser.add_argument(
        "--from-zone",
        default="UTC",
        help="Zone used to interpret --at when it has no offset (default: UTC).",
    )
    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="Print the known friendly region keys and exit.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_regions:
        for key, iana in sorted(REGIONS.items()):
            print(f"{key:<14} {iana}")
        return 0

    try:
        moment = parse_datetime(args.at, args.from_zone) if args.at else now()
    except (ValueError, ZoneInfoNotFoundError) as exc:
        parser.error(str(exc))

    try:
        rows = local_times(moment, args.regions or None)
    except ZoneInfoNotFoundError as exc:
        parser.error(str(exc))

    width = max(len(name) for name, _ in rows)
    for name, rendered in rows:
        print(f"{name:<{width}}  {rendered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
