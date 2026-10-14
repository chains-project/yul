"""Fetch a URL using a pooled, retrying urllib3 client."""

from __future__ import annotations

import argparse
import logging
import sys

from http_client.client import build_pool_manager, build_retry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--pool-size", type=int, default=10)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    # urllib3 logs connection reuse and retry attempts at DEBUG.
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    http = build_pool_manager(
        maxsize=args.pool_size,
        retries=build_retry(total=args.retries),
    )
    try:
        resp = http.request(args.method, args.url, preload_content=False)
        try:
            print(f"{resp.status} {resp.reason}", file=sys.stderr)
            for chunk in resp.stream(64 * 1024):
                sys.stdout.buffer.write(chunk)
        finally:
            resp.release_conn()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        http.clear()

    return 0 if resp.status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
