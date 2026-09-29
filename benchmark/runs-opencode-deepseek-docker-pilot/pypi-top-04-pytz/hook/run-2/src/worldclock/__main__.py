"""Command-line entry point: show one instant across world regions."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from worldclock.tz import convert

DEFAULT_REGIONS = (
    "UTC",
    "America/New_York",
    "Europe/London",
    "Asia/Tokyo",
    "Australia/Sydney",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldclock",
        description="Show the current time (or a given instant) across world regions.",
    )
    parser.add_argument(
        "regions",
        nargs="*",
        default=list(DEFAULT_REGIONS),
        metavar="REGION",
        help="IANA timezone names (default: a handful of world regions)",
    )
    parser.add_argument(
        "--at",
        metavar="ISO8601",
        help="instant to display; naive values are treated as UTC (default: now)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.at:
        moment = datetime.fromisoformat(args.at)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
    else:
        moment = datetime.now(timezone.utc)

    for region in args.regions:
        local = convert(moment, region)
        print(f"{region:<20} {local.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
