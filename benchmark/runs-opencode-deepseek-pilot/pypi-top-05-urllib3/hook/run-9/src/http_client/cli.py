"""Command-line entry point for the pooled HTTP client."""

from __future__ import annotations

import argparse
import sys

from .client import HttpClient, build_retries


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a URL with connection pooling and retries.")
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("--num-pools", type=int, default=10, help="Number of connection pools")
    parser.add_argument("--maxsize", type=int, default=10, help="Max connections per pool")
    parser.add_argument("--retries", type=int, default=5, help="Total retry attempts")
    parser.add_argument("--backoff", type=float, default=0.5, help="Retry backoff factor")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    args = parser.parse_args(argv)

    retries = build_retries(total=args.retries, backoff_factor=args.backoff)
    with HttpClient(
        num_pools=args.num_pools,
        maxsize=args.maxsize,
        retries=retries,
        timeout=args.timeout,
    ) as client:
        response = client.request(args.method, args.url)
        print(f"{response.status} {args.method} {args.url}")
        sys.stdout.buffer.write(response.data)
        print()
        return 0 if response.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
