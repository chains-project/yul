"""Command line entry point for fetching data from a REST API."""

import argparse
import json
import sys

from .client import ApiClient, ApiError


def build_parser():
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="Base URL of the API, e.g. https://api.example.com")
    parser.add_argument(
        "-p",
        "--path",
        default="",
        help="Path to request relative to the base URL.",
    )
    parser.add_argument(
        "-q",
        "--query",
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
        metavar="KEY:VALUE",
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
        "-i",
        "--indent",
        type=int,
        default=2,
        help="JSON indentation for output (default: 2).",
    )
    return parser


def _pairs(items, sep):
    result = {}
    for item in items:
        if sep not in item:
            raise ValueError("expected {0!r} in {1!r}".format(sep, item))
        key, value = item.split(sep, 1)
        result[key.strip()] = value.strip()
    return result


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = _pairs(args.query, "=")
        headers = _pairs(args.header, ":")
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    try:
        with ApiClient(args.url, timeout=args.timeout, headers=headers) as client:
            data = client.get(args.path, params=params)
    except ApiError as exc:
        print("error: {0}".format(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # network / decoding errors
        print("error: {0}".format(exc), file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=args.indent, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
