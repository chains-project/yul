"""Command line entry point for fetching data from a REST API."""

import argparse
import json
import sys

from api_fetch.client import ApiClient, ApiError


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="api-fetch",
        description="Fetch data from a REST API over HTTP.",
    )
    parser.add_argument("path", help="API path to request, e.g. /users")
    parser.add_argument(
        "--base-url",
        default="https://jsonplaceholder.typicode.com",
        help="API base URL (default: %(default)s)",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    try:
        with ApiClient(args.base_url, timeout=args.timeout) as client:
            data = client.get(args.path)
    except ApiError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
