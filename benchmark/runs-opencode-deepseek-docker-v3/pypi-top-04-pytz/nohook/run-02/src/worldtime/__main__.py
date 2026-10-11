"""Command line: show a moment across world regions."""

from __future__ import annotations

import argparse
from datetime import datetime

from .timezones import REGIONS, convert, now_in, parse_iso


def _offset_text(moment: datetime) -> str:
    raw = moment.strftime("%z")
    return f"{raw[:3]}:{raw[3:]}" if raw else ""


def _format(region: str, moment: datetime) -> str:
    abbr = moment.tzname() or ""
    return (
        f"{region:<12} {moment:%Y-%m-%d %H:%M:%S} "
        f"{_offset_text(moment):>6} {abbr}"
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show a time across world regions")
    parser.add_argument(
        "--at",
        metavar="ISO8601",
        help="aware timestamp to convert (default: now)",
    )
    parser.add_argument(
        "--region",
        action="append",
        dest="regions",
        help="region to include; repeatable (default: all known regions)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    regions = args.regions or list(REGIONS)

    if args.at is not None:
        moment = parse_iso(args.at)
        for region in regions:
            print(_format(region, convert(moment, region)))
    else:
        for region in regions:
            print(_format(region, now_in(region)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
