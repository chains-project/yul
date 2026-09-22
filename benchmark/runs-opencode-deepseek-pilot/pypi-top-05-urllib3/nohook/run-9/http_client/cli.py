"""Command line entrypoint for the pooled HTTP client."""

import argparse
import sys

import urllib3

from .client import HttpClient, HttpConfig


def build_parser():
    parser = argparse.ArgumentParser(
        description="Fetch a URL using pooled connections with automatic retries."
    )
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("--retries", type=int, default=3, help="Retry attempts (default: 3)")
    parser.add_argument(
        "--backoff-factor",
        type=float,
        default=0.5,
        help="Exponential backoff factor (default: 0.5)",
    )
    parser.add_argument("--maxsize", type=int, default=10, help="Connections per host pool")
    parser.add_argument("--timeout", type=float, default=30.0, help="Read timeout in seconds")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    config = HttpConfig(
        retries=args.retries,
        backoff_factor=args.backoff_factor,
        maxsize=args.maxsize,
        read_timeout=args.timeout,
    )

    try:
        with HttpClient(config) as client:
            response = client.request(args.method, args.url)
    except urllib3.exceptions.HTTPError as exc:
        sys.stderr.write("request failed: {0}\n".format(exc))
        return 1

    sys.stdout.write("HTTP {0}\n".format(response.status))
    body = response.data
    if body:
        sys.stdout.write(body.decode("utf-8", errors="replace"))
        sys.stdout.write("\n")
    return 0 if response.status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
