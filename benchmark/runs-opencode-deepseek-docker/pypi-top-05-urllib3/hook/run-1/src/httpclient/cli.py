from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from httpclient.client import HTTPClient


def _parse_headers(items: List[str]):
    headers = {}
    for item in items:
        key, separator, value = item.partition(":")
        if not separator:
            raise SystemExit(f"invalid header (expected 'Name: value'): {item!r}")
        headers[key.strip()] = value.strip()
    return headers


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="httpclient",
        description="Issue an HTTP request with connection pooling and automatic retries.",
    )
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("-H", "--header", action="append", default=[])
    parser.add_argument("-d", "--data", default=None)
    parser.add_argument("--retries", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress response headers")
    args = parser.parse_args(argv)

    with HTTPClient(headers=_parse_headers(args.header)) as client:
        response = client.request(
            args.method,
            args.url,
            retries=args.retries,
            timeout=args.timeout,
            body=args.data,
        )
        if not args.quiet:
            sys.stderr.write(f"HTTP {response.status} {response.reason}\n")
            for key, value in response.headers.items():
                sys.stderr.write(f"{key}: {value}\n")
            sys.stderr.write("\n")
        sys.stdout.buffer.write(response.data)
        sys.stdout.buffer.write(b"\n")
    return 0 if response.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
