"""Command-line entry point for fetching data from a REST API."""

from __future__ import annotations

import argparse
import json
import sys

from .client import RestClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="Full URL of the REST endpoint to fetch")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter (repeatable)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Request header (repeatable)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON output indentation (default: 2)",
    )
    return parser


def _parse_pairs(pairs: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise SystemExit(f"invalid KEY=VALUE pair: {pair!r}")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    params = _parse_pairs(args.param)
    headers = _parse_pairs(args.header)

    try:
        with RestClient(headers=headers, timeout=args.timeout) as client:
            data = client.get(args.url, params=params)
    except Exception as exc:  # noqa: BLE001 - surface any failure to the user
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=args.indent, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
