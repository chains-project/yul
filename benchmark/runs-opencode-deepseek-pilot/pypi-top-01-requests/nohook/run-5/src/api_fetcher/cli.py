"""Command line interface for fetching data from a REST API."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, Optional, Sequence

from .client import DEFAULT_TIMEOUT, ApiError, fetch_json


def _parse_params(items: Sequence[str]) -> Dict[str, str]:
    params: Dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            raise ValueError(f"expected KEY=VALUE for query parameter, got {item!r}")
        params[key] = value
    return params


def _parse_headers(items: Sequence[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition(":")
        if not sep:
            key, sep, value = item.partition("=")
        if not sep:
            raise ValueError(f"expected 'KEY: VALUE' for header, got {item!r}")
        headers[key.strip()] = value.strip()
    return headers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="REST API endpoint to fetch")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="request header (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="request timeout in seconds (default: %(default)s)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = fetch_json(
            args.url,
            params=_parse_params(args.param),
            headers=_parse_headers(args.header),
            timeout=args.timeout,
        )
    except (ApiError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
