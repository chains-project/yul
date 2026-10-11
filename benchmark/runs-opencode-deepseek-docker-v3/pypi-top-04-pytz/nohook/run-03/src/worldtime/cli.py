"""Command-line entry point: print a world clock."""

from __future__ import annotations

import argparse
import sys

from worldtime.converter import DEFAULT_REGIONS, parse_iso, world_clock


def _parse_region(value: str) -> tuple[str, str]:
    name, _, zone = value.partition("=")
    if not name or not zone:
        raise argparse.ArgumentTypeError("regions must be NAME=AREA/CITY")
    return name.strip(), zone.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldtime",
        description="Show timezone-aware times across world regions.",
    )
    parser.add_argument(
        "-a",
        "--at",
        metavar="ISO8601",
        help="convert a specific instant, e.g. 2026-03-08T01:30:00-05:00",
    )
    parser.add_argument(
        "-r",
        "--region",
        action="append",
        type=_parse_region,
        default=[],
        metavar="NAME=ZONE",
        help="add/replace a region (repeatable); defaults are used if none given",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    regions = dict(DEFAULT_REGIONS)
    for name, zone in args.region:
        regions[name] = zone

    try:
        instant = parse_iso(args.at) if args.at else None
        clock = world_clock(instant, regions)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    width = max(len(name) for name in clock)
    for name, dt in clock.items():
        print(f"{name:<{width}}  {dt:%Y-%m-%d %H:%M:%S %Z}  ({dt.isoformat()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
