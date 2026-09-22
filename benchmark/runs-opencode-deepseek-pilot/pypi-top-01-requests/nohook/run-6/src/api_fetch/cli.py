"""Command line entry point for api-fetch."""

from __future__ import annotations

import argparse
import json
import sys

from .client import ApiError, fetch_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetch",
        description="Fetch JSON from a REST API over HTTP.",
    )
    parser.add_argument("url", help="URL of the REST API endpoint")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="request header (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: %(default)s)",
    )
    return parser


def _parse_pairs(pairs: list[str], option: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in pairs:
        if "=" not in item:
            raise SystemExit(f"{option} expects KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        parsed[key] = value
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    params = _parse_pairs(args.param, "--param")
    headers = _parse_pairs(args.header, "--header")

    try:
        data = fetch_json(
            args.url,
            params=params or None,
            headers=headers or None,
            timeout=args.timeout,
        )
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
