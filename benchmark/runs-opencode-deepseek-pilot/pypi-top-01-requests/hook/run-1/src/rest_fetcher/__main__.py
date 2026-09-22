import argparse
import json
import sys

from .client import APIError, fetch_json


def _parse_pairs(values):
    pairs = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError(f"expected KEY=VALUE, got {value!r}")
        key, _, val = value.partition("=")
        pairs[key] = val
    return pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch JSON data from a REST API.")
    parser.add_argument("url")
    parser.add_argument("-p", "--param", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("-H", "--header", action="append", default=[], metavar="NAME=VALUE")
    parser.add_argument("-t", "--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    try:
        params = _parse_pairs(args.param)
        headers = _parse_pairs(args.header)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    try:
        data = fetch_json(args.url, params=params, headers=headers, timeout=args.timeout)
    except APIError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
