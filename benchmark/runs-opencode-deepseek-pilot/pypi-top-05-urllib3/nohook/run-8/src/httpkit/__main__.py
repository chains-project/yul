import argparse
import sys

from .client import HttpClient


def build_parser():
    parser = argparse.ArgumentParser(
        prog="httpkit", description="Fetch a URL with pooling and retries."
    )
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("-d", "--data", default=None)
    parser.add_argument(
        "-r", "--retries", type=int, default=3, help="maximum retry attempts"
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=30.0, help="read timeout in seconds"
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    with HttpClient(retries=_retries(args.retries), timeout=args.timeout) as client:
        response = client.request(args.method, args.url, body=args.data)
    sys.stdout.write(response.data.decode("utf-8", "replace"))
    return 0 if response.status < 400 else 1


def _retries(total):
    from .client import default_retries

    return default_retries(total=total)


if __name__ == "__main__":
    sys.exit(main())
