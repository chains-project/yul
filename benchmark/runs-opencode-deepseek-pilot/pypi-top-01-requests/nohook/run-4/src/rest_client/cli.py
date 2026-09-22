"""Command-line entry point for fetching data from a REST API."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .client import ApiError, RestClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest-client",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("path", help="API path to request, e.g. /users/1")
    parser.add_argument(
        "--base-url",
        default="https://jsonplaceholder.typicode.com",
        help="Root URL of the API (default: %(default)s)",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter; may be given more than once.",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Extra request header; may be given more than once.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: %(default)s)",
    )
    return parser


def _parse_pairs(items: List[str]) -> dict:
    pairs = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            raise SystemExit(f"expected KEY=VALUE, got {item!r}")
        pairs[key] = value
    return pairs


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    params = _parse_pairs(args.param)
    headers = _parse_pairs(args.header)

    try:
        with RestClient(
            args.base_url, timeout=args.timeout, headers=headers
        ) as client:
            data = client.get(args.path, params=params)
    except (ApiError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
