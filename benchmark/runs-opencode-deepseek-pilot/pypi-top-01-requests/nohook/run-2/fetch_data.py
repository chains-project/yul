#!/usr/bin/env python3
"""Fetch data from a REST API over HTTP."""

import argparse
import json
import sys

import requests


def fetch(url, params=None, timeout=30.0):
    """Fetch JSON data from the given URL.

    Raises requests.RequestException on transport or HTTP errors.
    """
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def parse_params(items, parser):
    params = {}
    for item in items:
        if "=" not in item:
            parser.error("invalid parameter %r, expected KEY=VALUE" % item)
        key, value = item.split("=", 1)
        params[key] = value
    return params


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="REST API endpoint to fetch")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=30.0,
        help="request timeout in seconds (default: 30)",
    )
    args = parser.parse_args(argv)

    params = parse_params(args.param, parser)

    try:
        data = fetch(args.url, params=params or None, timeout=args.timeout)
    except requests.RequestException as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
