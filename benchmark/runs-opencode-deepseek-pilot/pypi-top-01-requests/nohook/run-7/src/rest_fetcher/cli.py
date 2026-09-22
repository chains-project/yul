"""Command line interface for rest-fetcher."""

from __future__ import annotations

import argparse
import json
import sys

from .client import ApiError, fetch_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="The API endpoint to fetch.")
    parser.add_argument(
        "-X",
        "--method",
        default="GET",
        help="HTTP method to use (default: GET).",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY:VALUE",
        help="Request header, may be repeated.",
    )
    parser.add_argument(
        "-q",
        "--query",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query string parameter, may be repeated.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10).",
    )
    return parser


def _parse_pairs(items: list[str], separator: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition(separator)
        if not sep:
            raise SystemExit(f"Invalid value {item!r}; expected KEY{separator}VALUE")
        parsed[key.strip()] = value.strip()
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    headers = _parse_pairs(args.header, ":")
    params = _parse_pairs(args.query, "=")

    try:
        data = fetch_json(
            args.url,
            method=args.method,
            params=params,
            headers=headers,
            timeout=args.timeout,
        )
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
