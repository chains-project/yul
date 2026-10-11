"""CLI: verify an HTTPS URL against certifi's root CA bundle."""

from __future__ import annotations

import argparse
import socket
import ssl
import sys
import urllib.error
import urllib.request

from .verify import build_ssl_context, ca_bundle_path


def verify(url: str, timeout: float = 10.0) -> None:
    context = build_ssl_context()
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, context=context, timeout=timeout) as response:
        print(f"OK {response.status} {url}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="HTTPS URL to verify")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--show-bundle",
        action="store_true",
        help="Print the CA bundle path and exit",
    )
    args = parser.parse_args(argv)

    if args.show_bundle:
        print(ca_bundle_path())
        return 0

    if not args.url:
        parser.error("the following arguments are required: url")
    if not args.url.startswith("https://"):
        parser.error("url must use https://")

    try:
        verify(args.url, timeout=args.timeout)
    except (urllib.error.URLError, ssl.SSLError, socket.timeout) as exc:
        print(f"FAIL {args.url}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
