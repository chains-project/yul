"""Fetch HTTPS resources against a trusted, up-to-date root CA bundle."""

from __future__ import annotations

import argparse
import ssl
import sys
import urllib.request
from typing import Optional

import certifi

__version__ = "0.1.0"


def create_context() -> ssl.SSLContext:
    """Return an SSL context that trusts certifi's Mozilla root bundle."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, *, timeout: float = 30.0, user_agent: Optional[str] = None) -> bytes:
    """Fetch ``url`` over HTTPS, verifying the certificate chain via certifi."""
    headers = {"User-Agent": user_agent} if user_agent else {}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, context=create_context(), timeout=timeout) as response:
        return response.read()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="https-verify", description=__doc__)
    parser.add_argument("url", nargs="?", help="HTTPS URL to fetch")
    parser.add_argument("-o", "--output", help="write response body to this file")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--user-agent", default=None)
    parser.add_argument("--ca-bundle", action="store_true", help="print CA bundle path and exit")
    args = parser.parse_args(argv)

    if args.ca_bundle:
        print(certifi.where())
        return 0

    if not args.url:
        parser.error("the following arguments are required: url")

    try:
        body = fetch(args.url, timeout=args.timeout, user_agent=args.user_agent)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "wb") as handle:
            handle.write(body)
    else:
        sys.stdout.buffer.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
