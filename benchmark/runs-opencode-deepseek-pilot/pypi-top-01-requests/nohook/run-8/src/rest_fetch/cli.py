"""Command line entry point for fetching JSON from a REST endpoint."""

import argparse
import json
import sys

from .client import ApiError, RestClient


def build_parser():
    parser = argparse.ArgumentParser(
        prog="rest-fetch",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="Absolute URL or path to fetch.")
    parser.add_argument(
        "-b",
        "--base-url",
        default="",
        help="Base URL used when a relative path is given.",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter (repeatable).",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10).",
    )
    return parser


def parse_params(pairs):
    params = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError("invalid parameter {0!r}, expected KEY=VALUE".format(pair))
        key, value = pair.split("=", 1)
        params[key] = value
    return params


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        params = parse_params(args.param)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    client = RestClient(args.base_url, timeout=args.timeout)
    try:
        data = client.get(args.url, params=params or None)
    except ApiError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        client.close()

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
