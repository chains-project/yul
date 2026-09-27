from __future__ import annotations

import argparse
import json
import os
import sys

from .client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetch",
        description="Fetch JSON from a REST API over HTTP.",
    )
    parser.add_argument("path", help="API path, e.g. /users")
    parser.add_argument(
        "-b",
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
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: 10)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.base_url:
        parser.error("--base-url is required (or set API_BASE_URL)")

    params: dict[str, str] = {}
    for item in args.param:
        key, sep, value = item.partition("=")
        if not sep:
            parser.error(f"invalid --param {item!r}, expected KEY=VALUE")
        params[key] = value

    try:
        data = ApiClient(args.base_url, timeout=args.timeout).get(
            args.path, params=params
        )
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
