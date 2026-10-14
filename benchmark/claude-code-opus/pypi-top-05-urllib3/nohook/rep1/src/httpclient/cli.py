"""Command-line entry point."""

from __future__ import annotations

import argparse
import logging
import sys

from httpclient.client import build_pool_manager, build_retry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch URLs over pooled connections.")
    parser.add_argument("urls", nargs="+", help="URLs to fetch")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--backoff", type=float, default=0.5)
    parser.add_argument("--pool-size", type=int, default=10)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="log connection reuse and retries")
    args = parser.parse_args(argv)

    if args.verbose:
        # urllib3 logs new connections and retry attempts at DEBUG.
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    http = build_pool_manager(
        maxsize=args.pool_size,
        retries=build_retry(total=args.retries, backoff_factor=args.backoff),
    )

    exit_code = 0
    with http:
        for url in args.urls:
            try:
                resp = http.request(args.method, url, preload_content=False)
            except Exception as exc:  # MaxRetryError, NewConnectionError, etc.
                print(f"{url}: ERROR {exc}", file=sys.stderr)
                exit_code = 1
                continue
            try:
                size = sum(len(chunk) for chunk in resp.stream(64 * 1024))
            finally:
                resp.release_conn()  # Return the connection to the pool.
            history = len(resp.retries.history) if resp.retries else 0
            print(f"{url}: {resp.status} ({size} bytes, {history} retries)")
            if resp.status >= 400:
                exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
