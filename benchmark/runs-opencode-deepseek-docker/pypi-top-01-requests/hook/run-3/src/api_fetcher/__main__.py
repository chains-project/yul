"""Command line entry point: fetch JSON from a URL and print it."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, List, Optional

from .client import ApiClient, ApiError


def _parse_pairs(items: Iterable[str], separator: str) -> dict:
    pairs: dict = {}
    for item in items:
        key, found, value = item.partition(separator)
        if not found:
            raise SystemExit(f"Invalid value {item!r}; expected KEY{separator}VALUE")
        pairs[key.strip()] = value.strip()
    return pairs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON from a REST API over HTTP and print it.",
    )
    parser.add_argument("url", help="absolute URL to fetch")
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="NAME:VALUE",
        help="request header (repeatable)",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: 10)",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    headers = _parse_pairs(args.header, ":")
    params = _parse_pairs(args.param, "=")

    try:
        with ApiClient(
            args.url, headers=headers, timeout=args.timeout
        ) as client:
            data = client.get(params=params)
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
