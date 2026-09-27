"""Command-line entry point for fetching data from a REST API."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch JSON data from a REST API.")
    parser.add_argument("path", help="API path, e.g. /users/1")
    parser.add_argument("--base-url", required=True, help="API base URL")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter (repeatable)",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        params = dict(item.split("=", 1) for item in args.param)
    except ValueError:
        print("Invalid --param, expected KEY=VALUE", file=sys.stderr)
        return 2

    client = ApiClient(args.base_url, timeout=args.timeout)
    try:
        data = client.get(args.path, params=params)
    except ApiError as exc:
        print(exc, file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0
