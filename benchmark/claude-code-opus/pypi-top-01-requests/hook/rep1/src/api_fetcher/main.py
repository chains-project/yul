"""Command-line entry point."""

import argparse
import json
import logging
import os
import sys

import httpx

from api_fetcher.client import DEFAULT_TIMEOUT, ApiClient

log = logging.getLogger("api_fetcher")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch JSON from a REST API endpoint.")
    parser.add_argument("path", help="Endpoint path, e.g. /users")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("API_BASE_URL"),
        help="API base URL (default: $API_BASE_URL)",
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT, help="Request timeout in seconds"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if not args.base_url:
        log.error("No base URL given; pass --base-url or set API_BASE_URL")
        return 2

    token = os.environ.get("API_TOKEN")
    try:
        with ApiClient(args.base_url, token=token, timeout=args.timeout) as client:
            data = client.get(args.path)
    except httpx.HTTPStatusError as e:
        log.error("HTTP %s from %s", e.response.status_code, e.request.url)
        return 1
    except httpx.RequestError as e:
        log.error("Request failed: %s", e)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
