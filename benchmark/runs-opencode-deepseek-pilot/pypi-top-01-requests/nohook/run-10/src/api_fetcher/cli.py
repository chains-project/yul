"""Command line entry point for fetching data from a REST API."""

import argparse
import json
import sys

from .client import ApiError, fetch_json


def build_parser():
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="URL of the REST endpoint to fetch.")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter (repeatable).",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Request header (repeatable).",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10).",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for pretty-printed output (default: 2).",
    )
    return parser


def _parse_pairs(items, option):
    pairs = {}
    for item in items:
        if "=" not in item:
            raise SystemExit("Invalid %s %r, expected KEY=VALUE" % (option, item))
        key, value = item.split("=", 1)
        pairs[key] = value
    return pairs


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

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
        print("error: %s" % exc, file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=args.indent, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
