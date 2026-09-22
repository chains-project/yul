"""Command-line entry point for simple fetches."""

from __future__ import annotations

import argparse
import sys

from http_client.client import HttpClient


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a URL using a pooled, retrying HTTP client.")
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    args = parser.parse_args(argv)

    with HttpClient() as client:
        response = client.request(args.method, args.url)
        sys.stdout.write(response.data.decode("utf-8", errors="replace"))
        sys.stdout.write("\n")
        return 0 if response.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
