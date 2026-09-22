"""Command line entry point: fetch one or more URLs using a pooled client."""

from __future__ import annotations

import argparse
import sys

import urllib3

from http_client.client import HttpClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="http-client",
        description="Fetch URLs with connection pooling and automatic retries.",
    )
    parser.add_argument("urls", nargs="+", help="URLs to fetch")
    parser.add_argument(
        "--retries", type=int, default=3, help="total retries per request"
    )
    parser.add_argument(
        "--backoff", type=float, default=0.5, help="retry backoff factor"
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="connect/read timeout in seconds"
    )
    parser.add_argument(
        "--method", default="GET", help="HTTP method to use (default: GET)"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    with HttpClient(
        total_retries=args.retries,
        backoff_factor=args.backoff,
        timeout=args.timeout,
    ) as client:
        exit_code = 0
        for url in args.urls:
            try:
                response = client.request(args.method, url)
            except urllib3.exceptions.HTTPError as exc:
                print(f"{url}: request failed: {exc}", file=sys.stderr)
                exit_code = 1
                continue
            print(f"{url}: {response.status} ({len(response.data)} bytes)")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
