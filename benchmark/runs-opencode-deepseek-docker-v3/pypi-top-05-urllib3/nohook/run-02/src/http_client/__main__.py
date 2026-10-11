from __future__ import annotations

import argparse
import sys

from .client import HttpClient, PoolConfig, RetryPolicy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="http-client",
        description="Perform an HTTP request with pooled connections and retries.",
    )
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("-d", "--data", default=None, help="Request body")
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Maximum number of retries (default: 3)",
    )
    parser.add_argument(
        "--maxsize",
        type=int,
        default=10,
        help="Max pooled connections per host (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Read/connect timeout in seconds (default: 10)",
    )
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    pool = PoolConfig(maxsize=args.maxsize, retries=RetryPolicy(total=args.retries))
    with HttpClient(pool=pool, timeout=args.timeout, verify=not args.insecure) as client:
        response = client.request(args.method, args.url, body=args.data)
        try:
            sys.stdout.buffer.write(response.data)
            sys.stdout.write("\n")
        finally:
            response.release_conn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
