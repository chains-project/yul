"""Command-line entry point for api-fetcher."""

from __future__ import annotations

import argparse
import json
import sys

from .fetcher import ApiError, fetch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch data from a REST API over HTTP.",
    )
    parser.add_argument(
        "path",
        help="API path or absolute URL to fetch (e.g. /users/1).",
    )
    parser.add_argument(
        "-b",
        "--base-url",
        help="Base URL of the API. Defaults to the API_BASE_URL env var.",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter. May be repeated.",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Request header. May be repeated.",
    )
    parser.add_argument(
        "--token",
        help="Bearer token. Defaults to the API_TOKEN env var.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30).",
    )
    return parser


def _parse_pairs(items: list[str], flag: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"error: {flag} expects KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        parsed[key] = value
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        data = fetch(
            args.path,
            base_url=args.base_url,
            params=_parse_pairs(args.param, "--param"),
            headers=_parse_pairs(args.header, "--header"),
            token=args.token,
            timeout=args.timeout,
        )
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
