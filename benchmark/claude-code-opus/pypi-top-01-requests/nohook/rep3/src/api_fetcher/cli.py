"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from api_fetcher.client import DEFAULT_TIMEOUT, ApiClient, ApiError

log = logging.getLogger("api_fetcher")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch JSON from a REST API endpoint.")
    parser.add_argument("path", help="Endpoint path, e.g. /users/1")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("API_BASE_URL"),
        help="API base URL (default: $API_BASE_URL)",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter (repeatable)",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("-o", "--output", help="Write JSON to this file instead of stdout")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    if not args.base_url:
        parser.error("--base-url or API_BASE_URL is required")
    for item in args.param:
        if "=" not in item:
            parser.error(f"invalid --param {item!r}, expected KEY=VALUE")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    params = dict(item.split("=", 1) for item in args.param)
    token = os.environ.get("API_TOKEN")

    try:
        with ApiClient(args.base_url, token=token, timeout=args.timeout) as client:
            data = client.get(args.path, params=params or None)
    except ApiError as exc:
        log.error("%s", exc)
        return 1

    text = json.dumps(data, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
