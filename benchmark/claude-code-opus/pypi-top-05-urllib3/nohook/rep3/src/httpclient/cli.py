"""Command-line entry point."""

from __future__ import annotations

import argparse
import logging
import sys

from httpclient.client import build_pool_manager, build_retry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch URLs over a pooled, retrying connection.")
    parser.add_argument("urls", nargs="+", help="URLs to GET")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--backoff", type=float, default=0.5)
    parser.add_argument("--pool-size", type=int, default=10)
    parser.add_argument("-v", "--verbose", action="store_true", help="log connection/retry activity")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    http = build_pool_manager(
        maxsize=args.pool_size,
        retries=build_retry(total=args.retries, backoff_factor=args.backoff),
    )

    exit_code = 0
    with http:
        for url in args.urls:
            try:
                resp = http.request("GET", url, preload_content=True)
            except Exception as exc:  # MaxRetryError, etc.
                print(f"{url}\tERROR\t{exc}", file=sys.stderr)
                exit_code = 1
                continue
            print(f"{url}\t{resp.status}\t{len(resp.data)} bytes")
            if resp.status >= 400:
                exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
