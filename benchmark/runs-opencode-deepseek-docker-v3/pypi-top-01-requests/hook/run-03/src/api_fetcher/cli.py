"""Command line entry point: fetch a URL and print the JSON response."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .client import ApiError, RestClient


def parse_headers(values: Sequence[str]) -> dict:
    """Turn ``NAME:VALUE`` strings into a header mapping."""
    headers = {}
    for value in values:
        name, sep, header_value = value.partition(":")
        if not sep or not name.strip():
            raise ValueError(f"invalid header {value!r}, expected NAME:VALUE")
        headers[name.strip()] = header_value.strip()
    return headers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="Absolute URL or a path relative to --base-url")
    parser.add_argument("--base-url", help="Base URL prepended to relative paths")
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="Timeout in seconds"
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="NAME:VALUE",
        help="Extra request header (repeatable)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        headers = parse_headers(args.header)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        with RestClient(
            base_url=args.base_url,
            timeout=args.timeout,
            headers=headers,
        ) as client:
            data = client.get(args.url)
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
