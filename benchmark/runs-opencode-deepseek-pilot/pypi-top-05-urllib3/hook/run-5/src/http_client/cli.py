from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .client import HttpClient, build_retries


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pooled HTTP client with retries")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--backoff", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    retries = build_retries(total=args.retries, backoff_factor=args.backoff)
    with HttpClient(retries=retries, timeout=args.timeout) as client:
        response = client.request(args.method, args.url)
        sys.stdout.write(response.data.decode("utf-8", errors="replace"))
        return 0 if response.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
