"""Command-line entry point for a one-off pooled GET request."""

from __future__ import annotations

import argparse
import sys

from .client import build_session


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a URL over a pooled, retrying connection.")
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("--pool-size", type=int, default=10, help="max connections per host pool")
    parser.add_argument("--retries", type=int, default=3, help="number of retry attempts")
    parser.add_argument("--timeout", type=float, default=10.0, help="request timeout in seconds")
    args = parser.parse_args(argv)

    session = build_session(pool_maxsize=args.pool_size, max_retries=args.retries)
    try:
        response = session.request(args.method, args.url, timeout=args.timeout)
    except Exception as exc:  # noqa: BLE001 - surface any transport error to the user
        print(f"request failed: {exc}", file=sys.stderr)
        return 1

    print(f"{response.status_code} {response.reason}")
    print(response.text)
    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
