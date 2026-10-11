"""Command line entry point for fetching REST API data."""

from __future__ import annotations

import argparse
import json
import os
import sys

from api_client.client import APIClient
from api_client.config import Settings
from api_client.exceptions import APIError


def _parse_params(pairs: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise ValueError(f"invalid parameter {pair!r}, expected KEY=VALUE")
        params[key] = value
    return params


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-client",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("path", help="API path, e.g. /users")
    parser.add_argument("-p", "--param", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--base-url", default=os.environ.get("API_BASE_URL"))
    parser.add_argument("--timeout", type=float, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        params = _parse_params(args.param)
        settings = Settings.load(base_url=args.base_url, timeout=args.timeout)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        with APIClient(
            settings.base_url,
            token=settings.token,
            timeout=settings.timeout,
            retries=settings.retries,
        ) as client:
            data = client.get_json(args.path, params=params or None)
    except APIError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
