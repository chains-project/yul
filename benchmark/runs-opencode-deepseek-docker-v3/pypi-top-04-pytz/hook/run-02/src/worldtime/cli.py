"""Command-line interface for :mod:`worldtime`."""

from __future__ import annotations

import argparse
import json
from datetime import datetime

from worldtime import zones


def _parse_moment(value: str, region: str) -> datetime:
    """Parse an ISO-8601 string, localizing naive values to ``region``."""
    try:
        moment = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid ISO-8601 datetime: {value!r}"
        ) from exc
    if moment.tzinfo is None:
        moment = zones.localize(moment, region)
    return moment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="worldtime",
        description="Work with timezone-aware datetimes across world regions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_now = sub.add_parser("now", help="show the current time in regions")
    p_now.add_argument("regions", nargs="*", default=["utc"])
    p_now.add_argument("--json", action="store_true", help="emit JSON")

    p_convert = sub.add_parser("convert", help="convert a datetime between regions")
    p_convert.add_argument("value", help="ISO-8601 datetime")
    p_convert.add_argument("--from", dest="source", default="utc", help="source region")
    p_convert.add_argument("--to", dest="target", required=True, help="target region")
    p_convert.add_argument("--json", action="store_true", help="emit JSON")

    p_table = sub.add_parser("table", help="show all regions at one instant")
    p_table.add_argument("--at", help="ISO-8601 reference instant (default: now)")
    p_table.add_argument("--json", action="store_true", help="emit JSON")

    args = parser.parse_args(argv)

    if args.command == "now":
        rows = [
            {
                "region": region,
                "local_time": zones.now(region).isoformat(),
            }
            for region in args.regions
        ]
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for row in rows:
                print(f"{row['region']:<16} {row['local_time']}")
        return 0

    if args.command == "convert":
        moment = _parse_moment(args.value, args.source)
        converted = zones.to_region(moment, args.target)
        if args.json:
            print(json.dumps({"region": args.target, "local_time": converted.isoformat()}))
        else:
            print(converted.isoformat())
        return 0

    if args.command == "table":
        at = _parse_moment(args.at, "utc") if args.at else None
        rows = zones.table(at=at)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'REGION':<16} {'LOCAL TIME':<32} {'OFFSET':<7} DST")
            for row in rows:
                print(
                    f"{row['region']:<16} {row['local_time']:<32} "
                    f"{row['utc_offset']:<7} {row['dst']}"
                )
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
