"""Command line entry point: fetch JSON from a REST API over HTTP."""

import argparse
import json
import sys

from .client import DEFAULT_TIMEOUT, ApiError, fetch_json


def _pairs(values):
    result = {}
    for value in values:
        key, sep, item = value.partition("=")
        if not sep:
            raise argparse.ArgumentTypeError(
                "expected KEY=VALUE, got {!r}".format(value)
            )
        result[key] = item
    return result


def build_parser():
    parser = argparse.ArgumentParser(
        prog="api-client",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="full request URL")
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
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: %(default)s)",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        params = _pairs(args.param)
        headers = _pairs(args.header)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    try:
        data = fetch_json(
            args.url, params=params, headers=headers, timeout=args.timeout
        )
    except ApiError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    print(json.dumps(data, indent=args.indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
