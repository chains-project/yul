from __future__ import annotations

import argparse
import json
import sys

from rest_fetcher.client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="full URL or base URL when --path is given")
    parser.add_argument(
        "--path",
        default=None,
        help="path to request relative to the base URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="NAME:VALUE",
        help="extra request header, repeatable",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="query parameter, repeatable",
    )
    return parser


def _parse_headers(items: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in items:
        name, sep, value = item.partition(":")
        if not sep:
            raise ValueError(f"invalid header {item!r}, expected NAME:VALUE")
        headers[name.strip()] = value.strip()
    return headers


def _parse_params(items: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for item in items:
        name, sep, value = item.partition("=")
        if not sep:
            raise ValueError(f"invalid parameter {item!r}, expected NAME=VALUE")
        params[name.strip()] = value
    return params


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        headers = _parse_headers(args.header)
        params = _parse_params(args.param)
        if args.path:
            with ApiClient(args.url, headers=headers, timeout=args.timeout) as client:
                data = client.get(args.path, **params)
        else:
            from rest_fetcher.client import fetch_json

            data = fetch_json(args.url, headers=headers, params=params, timeout=args.timeout)
    except (ApiError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
