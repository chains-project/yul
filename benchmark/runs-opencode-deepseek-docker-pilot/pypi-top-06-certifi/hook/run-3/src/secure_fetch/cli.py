"""Command-line entry point for fetching a URL over verified HTTPS."""

from __future__ import annotations

import argparse
import ssl
import sys
import urllib.request

import certifi


def build_ssl_context() -> ssl.SSLContext:
    """Return an SSL context that trusts certifi's Mozilla CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(
    url: str,
    timeout: float = 30.0,
    context: ssl.SSLContext | None = None,
) -> bytes:
    """Fetch *url* over HTTPS and return the raw response body."""
    ctx = context if context is not None else build_ssl_context()
    with urllib.request.urlopen(url, timeout=timeout, context=ctx) as response:
        return response.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="secure-fetch",
        description="Fetch a URL over HTTPS using certifi's root CA bundle.",
    )
    parser.add_argument("url", help="HTTPS URL to fetch")
    parser.add_argument(
        "-o",
        "--output",
        help="write the response body to this file instead of stdout",
    )
    args = parser.parse_args(argv)

    try:
        body = fetch(args.url)
    except Exception as exc:
        print(f"secure-fetch: error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "wb") as handle:
            handle.write(body)
    else:
        sys.stdout.buffer.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
