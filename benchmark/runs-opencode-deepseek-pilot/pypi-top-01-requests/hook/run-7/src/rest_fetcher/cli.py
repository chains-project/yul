"""Command-line entry point for fetching data from a REST API."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .client import ApiError, RestClient


def _parse_header(value: str) -> "tuple[str, str]":
    if ":" not in value:
        raise argparse.ArgumentTypeError(
            "header must be in 'Name: value' form, got {!r}".format(value)
        )
    name, _, val = value.partition(":")
    return name.strip(), val.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rest-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="URL or path to request")
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
        type=_parse_header,
        metavar="NAME:VALUE",
        help="request header (repeatable)",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=10.0, help="timeout in seconds"
    )
    parser.add_argument(
        "-o", "--output", help="write the response body to this file instead of stdout"
    )
    parser.add_argument(
        "--compact", action="store_true", help="print compact JSON instead of indented"
    )
    return parser


def _parse_params(items: List[str]) -> "dict[str, str]":
    params = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            raise SystemExit("invalid --param {!r}, expected KEY=VALUE".format(item))
        params[key] = value
    return params


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    params = _parse_params(args.param)
    headers = dict(args.header) if args.header else None

    try:
        with RestClient(timeout=args.timeout) as client:
            data = client.get(args.url, params=params or None, headers=headers)
    except ApiError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    indent = None if args.compact else 2
    text = json.dumps(data, indent=indent)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
