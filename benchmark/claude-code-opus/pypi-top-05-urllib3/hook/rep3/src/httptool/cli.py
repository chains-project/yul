"""Command-line entry point."""

from __future__ import annotations

import argparse
import logging
import sys

from urllib3.exceptions import HTTPError

from httptool.client import ClientConfig, build_pool_manager


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch URLs over a pooled, retrying connection.")
    p.add_argument("urls", nargs="+", help="URLs to request")
    p.add_argument("-X", "--method", default="GET")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--backoff", type=float, default=0.5)
    p.add_argument("--pool-size", type=int, default=10, help="connections per host")
    p.add_argument("--connect-timeout", type=float, default=5.0)
    p.add_argument("--read-timeout", type=float, default=30.0)
    p.add_argument("-v", "--verbose", action="store_true", help="log connection/retry activity")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    config = ClientConfig(
        maxsize=args.pool_size,
        connect_timeout=args.connect_timeout,
        read_timeout=args.read_timeout,
        total_retries=args.retries,
        backoff_factor=args.backoff,
    )
    exit_code = 0
    with build_pool_manager(config) as http:
        for url in args.urls:
            try:
                resp = http.request(args.method, url)
            except HTTPError as exc:  # MaxRetryError, timeouts, protocol errors
                print(f"{url}: ERROR {exc}", file=sys.stderr)
                exit_code = 1
                continue
            print(f"{url}: {resp.status} ({len(resp.data)} bytes)")
            if resp.status >= 400:
                exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
