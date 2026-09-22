"""Fetch JSON data from a REST API over HTTP."""

import argparse
import json
import sys

import requests


def fetch_json(url, timeout=10, params=None):
    """GET a URL and return the decoded JSON body."""
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch JSON from a REST API.")
    parser.add_argument("url", help="API endpoint to fetch")
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="request timeout in seconds")
    args = parser.parse_args(argv)

    params = dict(p.split("=", 1) for p in args.param)

    try:
        data = fetch_json(args.url, timeout=args.timeout, params=params)
    except requests.RequestException as exc:
        print("request failed: {}".format(exc), file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
