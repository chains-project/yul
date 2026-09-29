"""Fetch a URL over HTTPS using certifi's trusted root CA bundle."""

from __future__ import annotations

import argparse
import ssl
import sys
import urllib.request

from .context import ca_bundle_path, create_context

__all__ = ["fetch", "main"]


def fetch(url: str, *, timeout: float = 30.0) -> bytes:
    """Fetch ``url`` over HTTPS, verifying the server certificate."""
    context = create_context()
    with urllib.request.urlopen(url, context=context, timeout=timeout) as response:
        return response.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch a URL over HTTPS, verifying the server certificate against "
            "certifi's up-to-date root CA bundle."
        )
    )
    parser.add_argument("url", nargs="?", help="the https:// URL to fetch")
    parser.add_argument("-t", "--timeout", type=float, default=30.0)
    parser.add_argument(
        "--ca-bundle",
        action="store_true",
        help="print the CA bundle path and exit",
    )
    args = parser.parse_args(argv)

    if args.ca_bundle:
        print(ca_bundle_path())
        return 0

    if not args.url:
        parser.error("the following arguments are required: url")

    try:
        body = fetch(args.url, timeout=args.timeout)
    except (ssl.SSLError, OSError) as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1

    sys.stdout.buffer.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
