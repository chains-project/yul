"""Command-line entry point for fetching an API resource."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API endpoint over HTTP.",
    )
    parser.add_argument("url", help="absolute endpoint URL to fetch")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter to send (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: 10)",
    )
    return parser


def parse_params(items: List[str]) -> dict:
    params = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep or not key:
            raise ValueError(f"invalid parameter {item!r}, expected KEY=VALUE")
        params[key] = value
    return params


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        params = parse_params(args.param)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        with ApiClient(timeout=args.timeout) as client:
            data = client.get(args.url, params=params or None)
    except (ApiError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
