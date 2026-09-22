"""Command-line entry point: fetch a URL using the pooled client."""

import argparse
import sys

from .client import HttpClient, HttpError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch a URL with pooling and retries.")
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--maxsize", type=int, default=10)
    args = parser.parse_args(argv)

    client = HttpClient(
        retries=args.retries,
        timeout=args.timeout,
        maxsize=args.maxsize,
    )
    try:
        response = client.get(args.url) if args.method == "GET" else client.request(args.method, args.url)
    except HttpError as exc:
        sys.stderr.write("%s\n" % exc)
        return 1
    finally:
        client.close()

    sys.stdout.write(response.data.decode("utf-8", "replace"))
    if not response.data.endswith(b"\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
