"""Command-line entry point: fetch a URL using the pooled client."""

import argparse
import sys

from .client import HttpClient


def build_parser():
    parser = argparse.ArgumentParser(
        prog="http-client",
        description="Fetch a URL with connection pooling and automatic retries.",
    )
    parser.add_argument("url", help="absolute URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("-d", "--data", default=None, help="request body")
    parser.add_argument("-H", "--header", action="append", default=[], help="extra header, 'Name: value'")
    parser.add_argument("-r", "--retries", type=int, default=5, help="max retry attempts (default: 5)")
    parser.add_argument("-t", "--timeout", type=float, default=30.0, help="timeout in seconds (default: 30)")
    parser.add_argument("--maxsize", type=int, default=10, help="connections kept per host pool")
    parser.add_argument("-k", "--insecure", action="store_true", help="skip TLS verification")
    parser.add_argument("-q", "--quiet", action="store_true", help="print status code only")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    headers = {}
    for raw in args.header:
        name, _, value = raw.partition(":")
        headers[name.strip()] = value.strip()

    client = HttpClient(
        maxsize=args.maxsize,
        retries=args.retries,
        timeout=args.timeout,
        verify=not args.insecure,
    )
    try:
        response = client.request(args.method, args.url, body=args.data, headers=headers or None)
        body = response.data
        if args.quiet:
            print(response.status)
        else:
            print("HTTP/{} {}".format(response.status, response.reason))
            for name, value in response.headers.items():
                print("{}: {}".format(name, value))
            print()
            sys.stdout.buffer.write(body)
            if not body.endswith(b"\n"):
                print()
        return 0 if response.status < 400 else 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
