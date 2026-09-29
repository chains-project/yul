"""Command line entry point: show or convert times across the world."""

from __future__ import annotations

import argparse
from datetime import datetime

from worldtime.convert import UTC, resolve_zone, to_zone

DEFAULT_ZONES = ("UTC", "America/New_York", "Europe/London", "Asia/Tokyo")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldtime",
        description="Convert timezone-aware datetimes across regions of the world.",
    )
    parser.add_argument(
        "zones",
        nargs="*",
        default=list(DEFAULT_ZONES),
        help="IANA timezone names (default: a few common regions)",
    )
    parser.add_argument(
        "--at",
        metavar="ISO",
        help="convert this ISO-8601 instant instead of the current time",
    )
    parser.add_argument(
        "--from",
        dest="source",
        metavar="ZONE",
        help="timezone the --at value is expressed in (default: UTC)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.at is not None:
        base = datetime.fromisoformat(args.at)
        if base.tzinfo is None:
            base = base.replace(tzinfo=resolve_zone(args.source or "UTC"))
        moment = base
    else:
        moment = datetime.now(UTC)

    width = max(len(name) for name in args.zones)
    for name in args.zones:
        local = to_zone(moment, name)
        print(f"{name:<{width}}  {local.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
