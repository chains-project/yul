"""Command-line entry point."""

import argparse
import json
import os
import sys

import httpx

from api_fetcher.client import ApiClient


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch JSON from a REST API endpoint.")
    parser.add_argument("path", help="Endpoint path, e.g. /users/1")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("API_BASE_URL", "https://jsonplaceholder.typicode.com"),
        help="API base URL (env: API_BASE_URL)",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter; may be repeated",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    params = dict(p.split("=", 1) for p in args.param)
    token = os.environ.get("API_TOKEN")

    try:
        with ApiClient(args.base_url, token=token, timeout=args.timeout) as client:
            data = client.get(args.path, params=params or None)
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code} from {e.request.url}", file=sys.stderr)
        return 1
    except httpx.HTTPError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
