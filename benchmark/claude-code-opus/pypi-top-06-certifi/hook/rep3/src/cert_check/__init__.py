"""Make HTTPS requests verified against the Mozilla CA bundle shipped by certifi."""

import ssl
import sys
import urllib.request

import certifi


def ssl_context() -> ssl.SSLContext:
    """Return a client SSL context that trusts only certifi's root certificates."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, timeout: float = 10.0) -> bytes:
    with urllib.request.urlopen(url, context=ssl_context(), timeout=timeout) as resp:
        return resp.read()


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.python.org"
    print(f"CA bundle: {certifi.where()} (certifi {certifi.__version__})")
    body = fetch(url)
    print(f"OK: {url} verified, {len(body)} bytes received")
