"""Command line entry point for fetching API data."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from .client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API.",
    )
    parser.add_argument("path", help="API path (or full URL) to fetch")
    parser.add_argument("-b", "--base-url", default="https://api.github.com", help="API base URL")
    parser.add_argument("-p", "--param", action="append", default=[], metavar="KEY=VALUE", help="query parameter (repeatable)")
    parser.add_argument("-H", "--header", action="append", default=[], metavar="KEY=VALUE", help="request header (repeatable)")
    parser.add_argument("-t", "--timeout", type=float, default=10.0, help="request timeout in seconds")
    return parser


def _parse_pairs(pairs: Sequence[str]) -> dict:
    parsed = {}
    for item in pairs:
        key, sep, value = item.partition("=")
        if not sep:
            raise SystemExit(f"invalid KEY=VALUE pair: {item!r}")
        parsed[key] = value
    return parsed


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    client = ApiClient(
        args.base_url,
        timeout=args.timeout,
        headers=_parse_pairs(args.header),
    )
    try:
        with client:
            data = client.get(args.path, params=_parse_pairs(args.param))
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
