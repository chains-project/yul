"""Command-line entry point for the worldclock project."""

from __future__ import annotations

import argparse
from datetime import datetime

from . import DEFAULT_ZONES, format_in_zone, local_time_in_zones


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldclock",
        description="Show the current time across world regions.",
    )
    parser.add_argument(
        "zones",
        nargs="*",
        default=list(DEFAULT_ZONES),
        metavar="ZONE",
        help="IANA timezone names (default: a small selection of regions)",
    )
    parser.add_argument(
        "-t",
        "--at",
        metavar="ISO8601",
        help="show times for a specific instant instead of now",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    when: datetime | None = None
    if args.at:
        when = datetime.fromisoformat(args.at)

    rows = local_time_in_zones(args.zones, when)
    width = max(len(name) for name in rows)
    for name, moment in rows.items():
        print(f"{name:<{width}}  {format_in_zone(moment, name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
