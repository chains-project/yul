"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from urllib3.exceptions import MaxRetryError

from http_client.client import build_pool_manager, build_retry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch URLs over a shared connection pool.")
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--backoff", type=float, default=0.5)
    parser.add_argument("--pool-size", type=int, default=10)
    args = parser.parse_args(argv)

    http = build_pool_manager(
        maxsize=args.pool_size,
        retries=build_retry(total=args.retries, backoff_factor=args.backoff),
    )

    exit_code = 0
    with http:
        for url in args.urls:
            try:
                resp = http.request("GET", url, preload_content=False)
                try:
                    body = resp.read()
                finally:
                    resp.release_conn()  # return the connection to the pool
                retried = len(resp.retries.history) if resp.retries else 0
                print(f"{resp.status} {url} ({len(body)} bytes, {retried} retries)")
                if resp.status >= 400:
                    exit_code = 1
            except MaxRetryError as exc:
                print(f"FAILED {url}: {exc.reason}", file=sys.stderr)
                exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
