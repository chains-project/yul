"""Fetch URLs over HTTPS, trusting certifi's bundled root certificates.

certifi ships the Mozilla CA bundle, so TLS verification stays current as long
as the dependency is upgraded: ``pip install --upgrade certifi``.
"""

from __future__ import annotations

import argparse
import ssl
import urllib.request

import certifi

DEFAULT_URL = "https://example.com"
DEFAULT_TIMEOUT = 10.0
USER_AGENT = "secure-https/0.1"


def build_ssl_context() -> ssl.SSLContext:
    """Return an SSL context that verifies peers against certifi's CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, timeout: float = DEFAULT_TIMEOUT) -> bytes:
    """Fetch *url* over HTTPS and return the response body."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(
        request, timeout=timeout, context=build_ssl_context()
    ) as response:
        return response.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--ca-bundle",
        action="store_true",
        help="print the path to certifi's CA bundle and exit",
    )
    args = parser.parse_args(argv)

    if args.ca_bundle:
        print(certifi.where())
        return 0

    try:
        body = fetch(args.url, timeout=args.timeout)
    except Exception as exc:  # noqa: BLE001 - surface any TLS/network failure
        print(f"error: {exc}")
        return 1

    print(f"ok: fetched {len(body)} bytes from {args.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
