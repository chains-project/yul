"""Fetch a URL over HTTPS, verifying the server against certifi's root CA bundle."""

import argparse
import ssl
import sys
import urllib.request

import certifi


def make_ssl_context() -> ssl.SSLContext:
    """Return an SSL context that trusts only the Mozilla roots shipped by certifi."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, timeout: float = 10.0) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout, context=make_ssl_context()) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default="https://www.python.org")
    args = parser.parse_args()

    print(f"Using CA bundle: {certifi.where()}", file=sys.stderr)
    body = fetch(args.url)
    print(f"Fetched {len(body)} bytes from {args.url}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
