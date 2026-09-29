"""Command-line entry point for fetching a resource."""

from __future__ import annotations

import argparse
import json
import os
import sys

from .client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON from a REST API over HTTP.",
    )
    parser.add_argument("path", help="Endpoint path or full URL to fetch")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("API_BASE_URL", ""),
        help="API base URL (default: $API_BASE_URL)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("API_TOKEN"),
        help="Bearer token (default: $API_TOKEN)",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter, repeatable",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10)",
    )
    return parser


def parse_params(pairs: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"invalid --param {pair!r}, expected KEY=VALUE")
        key, value = pair.split("=", 1)
        params[key] = value
    return params


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.path.startswith(("http://", "https://")):
        base_url, path = args.path, ""
    else:
        base_url, path = args.base_url, args.path

    if not base_url:
        parser.error("no base URL provided; pass --base-url or set API_BASE_URL")

    try:
        params = parse_params(args.param)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        with ApiClient(base_url, token=args.token, timeout=args.timeout) as client:
            data = client.get(path, params=params)
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
