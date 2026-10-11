"""Command-line entrypoint: ``api-fetcher <url>``."""

from __future__ import annotations

import argparse
import json
import sys

from api_fetcher.client import ApiError, fetch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY:VALUE",
        help="Header to send; may be repeated",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter; may be repeated",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")
    return parser


def _parse_pairs(items: list[str], separator: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition(separator)
        if not sep:
            raise SystemExit(f"invalid value {item!r}: expected KEY{separator}VALUE")
        result[key.strip()] = value.strip()
    return result


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        response = fetch(
            args.url,
            method=args.method.upper(),
            params=_parse_pairs(args.param, "="),
            headers=_parse_pairs(args.header, ":"),
            timeout=args.timeout,
        )
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    json.dump(response.data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
