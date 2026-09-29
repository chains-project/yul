from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from netclient import PooledHTTPClient, RetryConfig, TimeoutConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netclient", description="Issue a pooled HTTP request.")
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("-d", "--data", default=None)
    parser.add_argument("-H", "--header", action="append", default=[])
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--connect-timeout", type=float, default=5.0)
    parser.add_argument("--read-timeout", type=float, default=30.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    headers = {}
    for item in args.header:
        name, _, value = item.partition(":")
        headers[name.strip()] = value.strip()

    with PooledHTTPClient(
        retries=RetryConfig(total=args.max_retries),
        timeout=TimeoutConfig(connect=args.connect_timeout, read=args.read_timeout),
        headers=headers,
    ) as client:
        response = client.request(args.method, args.url, body=args.data)
        sys.stdout.write(response.data.decode("utf-8", errors="replace"))
        sys.stdout.write("\n")
        return 0 if response.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
