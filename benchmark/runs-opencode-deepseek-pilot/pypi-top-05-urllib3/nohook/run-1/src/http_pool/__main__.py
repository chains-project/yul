"""Command-line entry point for the pooled HTTP client."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .client import DEFAULT_RETRY, DEFAULT_TIMEOUT, HTTPError, HttpClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="http-pool",
        description="Fetch a URL using a connection-pooled, retrying HTTP client.",
    )
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="NAME:VALUE",
        help="request header (repeatable)",
    )
    parser.add_argument("-d", "--data", default=None, help="request body")
    parser.add_argument(
        "-t", "--timeout", type=float, default=DEFAULT_TIMEOUT, help="timeout in seconds"
    )
    parser.add_argument(
        "-r", "--retries", type=int, default=DEFAULT_RETRY.total, help="max retry attempts"
    )
    parser.add_argument("--json", action="store_true", help="pretty-print the JSON body")
    return parser


def _parse_headers(pairs: Sequence[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for pair in pairs:
        name, sep, value = pair.partition(":")
        if not sep:
            raise ValueError(f"invalid header {pair!r}, expected NAME:VALUE")
        headers[name.strip()] = value.strip()
    return headers


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        headers = _parse_headers(args.header)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    retries = DEFAULT_RETRY.new(total=args.retries) if args.retries != DEFAULT_RETRY.total else DEFAULT_RETRY

    with HttpClient(retries=retries, timeout=args.timeout, headers=headers) as client:
        try:
            response = client.request(args.method.upper(), args.url, body=args.data)
        except HTTPError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        body = response.data.decode("utf-8", errors="replace")
        if args.json:
            try:
                body = json.dumps(json.loads(body), indent=2, sort_keys=True)
            except ValueError:
                print("error: response is not valid JSON", file=sys.stderr)
                return 1

        print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
