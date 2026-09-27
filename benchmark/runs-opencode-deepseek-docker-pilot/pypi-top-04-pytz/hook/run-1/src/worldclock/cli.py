"""Command line interface for :mod:`worldclock`."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import List, Optional, Sequence

from worldclock.convert import (
    UnknownTimeZoneError,
    available_zones,
    convert,
    now_in,
    parse_iso,
)


def _format(value: datetime) -> str:
    offset = value.utcoffset()
    sign = "+" if offset is not None and offset.total_seconds() >= 0 else "-"
    if offset is not None:
        total = int(abs(offset.total_seconds()))
        hours, minutes = divmod(total // 60, 60)
        suffix = f"UTC{sign}{hours:02d}:{minutes:02d}"
    else:
        suffix = ""
    name = getattr(value.tzinfo, "key", None) or value.tzname() or "?"
    return f"{value:%Y-%m-%d %H:%M:%S} {suffix} ({name})"


def _cmd_now(args: argparse.Namespace) -> int:
    for zone in args.zones:
        print(f"{zone:<32} {_format(now_in(zone))}")
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    moment = parse_iso(args.timestamp, assume=args.source)
    print(f"{'source':<32} {_format(moment)}")
    for zone in args.targets:
        print(f"{zone:<32} {_format(convert(moment, zone))}")
    return 0


def _cmd_zones(args: argparse.Namespace) -> int:
    needle = (args.filter or "").lower()
    matches: List[str] = [
        zone for zone in available_zones() if needle in zone.lower()
    ]
    if not matches:
        print("no matching timezones", file=sys.stderr)
        return 1
    for zone in matches:
        print(zone)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldclock",
        description="Work with timezone-aware datetimes across world regions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    now_parser = sub.add_parser("now", help="current time in one or more zones")
    now_parser.add_argument("zones", nargs="+", help="IANA timezone names")
    now_parser.set_defaults(func=_cmd_now)

    convert_parser = sub.add_parser(
        "convert", help="convert an ISO-8601 timestamp between zones"
    )
    convert_parser.add_argument("timestamp", help="ISO-8601 timestamp")
    convert_parser.add_argument(
        "--from",
        dest="source",
        default="UTC",
        help="zone for naive timestamps (default: UTC)",
    )
    convert_parser.add_argument(
        "--to",
        dest="targets",
        action="append",
        required=True,
        help="target zone (repeatable)",
    )
    convert_parser.set_defaults(func=_cmd_convert)

    zones_parser = sub.add_parser("zones", help="list known timezones")
    zones_parser.add_argument("filter", nargs="?", help="substring to match")
    zones_parser.set_defaults(func=_cmd_zones)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UnknownTimeZoneError as exc:
        print(f"unknown timezone: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
