import argparse
import json
import sys

from .client import DEFAULT_RETRIES, DEFAULT_TIMEOUT, ApiError, RestClient


def build_parser():
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="full URL, or path appended to --base-url")
    parser.add_argument("--base-url", default="", help="base URL prepended to path")
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
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    return parser


def parse_pairs(pairs):
    result = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError("expected KEY=VALUE, got {!r}".format(pair))
        key, value = pair.split("=", 1)
        result[key] = value
    return result


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        params = parse_pairs(args.param)
        headers = parse_pairs(args.header)
    except ValueError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2

    with RestClient(
        base_url=args.base_url, timeout=args.timeout, retries=args.retries
    ) as client:
        try:
            data = client.get_json(args.url, params=params, headers=headers)
        except ApiError as exc:
            print("error: {}".format(exc), file=sys.stderr)
            return 1

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
