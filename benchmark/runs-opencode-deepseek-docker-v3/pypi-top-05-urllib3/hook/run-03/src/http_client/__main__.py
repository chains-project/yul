from __future__ import annotations

import argparse
import logging
import sys

from http_client.client import HttpClient, PoolConfig, RetryPolicy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="http-fetch", description="Fetch URLs with pooling and retries"
    )
    parser.add_argument("urls", nargs="+", help="One or more URLs to fetch")
    parser.add_argument("--retries", type=int, default=3, help="Total retry attempts (default: 3)")
    parser.add_argument(
        "--backoff", type=float, default=0.5, help="Retry backoff factor (default: 0.5)"
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="Per-request timeout in seconds"
    )
    parser.add_argument("--max-connections", type=int, default=10, help="Connections per host")
    parser.add_argument("--workers", type=int, default=None, help="Concurrent worker threads")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    pool = PoolConfig(
        maxsize=args.max_connections,
        timeout=args.timeout,
        retries=RetryPolicy(total=args.retries, backoff_factor=args.backoff),
    )

    exit_code = 0
    with HttpClient(pool) as client:
        responses = client.get_many(args.urls, max_workers=args.workers)
    for url, response in zip(args.urls, responses, strict=True):
        print(f"{response.status} {url} ({len(response.data)} bytes)")
        if response.status >= 400:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
