"""Command-line entry point for fetching data from a REST API."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, Optional, Sequence

from .client import DEFAULT_TIMEOUT, fetch_json


def _parse_pairs(
    parser: argparse.ArgumentParser,
    values: Sequence[str],
    flag: str,
) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for item in values:
        key, sep, value = item.partition("=")
        if not sep or not key:
            parser.error("invalid {} value {!r}; expected KEY=VALUE".format(flag, item))
        pairs[key] = value
    return pairs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="API endpoint URL")
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
        default=DEFAULT_TIMEOUT,
        help="request timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="write the JSON response to PATH instead of stdout",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    params = _parse_pairs(parser, args.param, "--param")
    headers = _parse_pairs(parser, args.header, "--header")

    try:
        data = fetch_json(
            args.url,
            params=params,
            headers=headers,
            timeout=args.timeout,
        )
    except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the CLI
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    payload = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
