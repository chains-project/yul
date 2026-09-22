"""Command-line entry point for the REST API fetcher."""

import argparse
import json
import sys

from .client import ApiClient, FetchError

DEFAULT_BASE_URL = "https://api.github.com"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="rest-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument(
        "path",
        help="API path to fetch, e.g. /repos/psf/requests",
    )
    parser.add_argument(
        "-b", "--base-url",
        default=DEFAULT_BASE_URL,
        help="API root URL (default: %(default)s)",
    )
    parser.add_argument(
        "-p", "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query parameter; may be repeated",
    )
    parser.add_argument(
        "-H", "--header",
        action="append",
        default=[],
        metavar="NAME:VALUE",
        help="Extra request header; may be repeated",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON response",
    )
    return parser


def _parse_params(items):
    params = {}
    for item in items:
        if "=" not in item:
            raise ValueError("invalid --param {!r}, expected KEY=VALUE".format(item))
        key, value = item.split("=", 1)
        params[key] = value
    return params


def _parse_headers(items):
    headers = {}
    for item in items:
        if ":" not in item:
            raise ValueError("invalid --header {!r}, expected NAME:VALUE".format(item))
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = _parse_params(args.param)
        headers = _parse_headers(args.header)
    except ValueError as exc:
        parser.error(str(exc))

    indent = 2 if args.pretty else None
    with ApiClient(args.base_url, timeout=args.timeout, headers=headers) as client:
        try:
            data = client.get(args.path, params=params)
        except FetchError as exc:
            print("error: {}".format(exc), file=sys.stderr)
            return 1

    print(json.dumps(data, indent=indent, sort_keys=bool(indent)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
