"""Command-line interface for :mod:`worldtime`."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .core import REGIONS, convert, current_time, parse


def _resolve(name: str) -> str:
    """Map a region alias to an IANA zone, otherwise treat it as a zone name."""
    return REGIONS.get(name.strip().lower(), name)


def _cmd_now(args: argparse.Namespace) -> int:
    zone = _resolve(args.where)
    moment = current_time(zone)
    print(moment.isoformat())
    return 0


def _cmd_regions(_: argparse.Namespace) -> int:
    for region, zone in sorted(REGIONS.items()):
        print(f"{region:<16} {zone}")
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    source = _resolve(args.source) if args.source else None
    target = _resolve(args.to)
    moment = parse(args.value, source)
    print(convert(moment, target).isoformat())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldtime",
        description="Work with timezone-aware datetimes across the world.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    now = sub.add_parser("now", help="show the current time in a region or zone")
    now.add_argument(
        "where",
        nargs="?",
        default="utc",
        help="region alias or IANA zone (default: utc)",
    )
    now.set_defaults(func=_cmd_now)

    conv = sub.add_parser("convert", help="convert an ISO 8601 timestamp")
    conv.add_argument("value", help="ISO 8601 timestamp, with or without offset")
    conv.add_argument("--to", required=True, help="target region or IANA zone")
    conv.add_argument(
        "--from",
        dest="source",
        default=None,
        help="zone to assume when the timestamp has no offset (default: UTC)",
    )
    conv.set_defaults(func=_cmd_convert)

    regions = sub.add_parser("regions", help="list built-in regions")
    regions.set_defaults(func=_cmd_regions)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (KeyError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
