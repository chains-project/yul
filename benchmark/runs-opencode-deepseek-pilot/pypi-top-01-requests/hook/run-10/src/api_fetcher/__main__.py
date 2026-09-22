"""Command line entry point: fetch a URL and print the JSON response."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .client import ApiClient, ApiError


def _parse_params(pairs: Sequence[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise argparse.ArgumentTypeError(f"expected KEY=VALUE, got {pair!r}")
        params[key] = value
    return params


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="request header (repeatable)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = _parse_params(args.param)
        headers = _parse_params(args.header)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    try:
        with ApiClient(timeout=args.timeout, headers=headers) as client:
            data = client.get(args.url, params=params or None)
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
