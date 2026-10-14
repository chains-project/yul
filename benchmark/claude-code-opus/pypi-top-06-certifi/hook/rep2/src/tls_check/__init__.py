"""Fetch an HTTPS URL, verifying the server against certifi's CA bundle."""

import argparse
import ssl
import sys
import urllib.error
import urllib.request

import certifi


def make_ssl_context() -> ssl.SSLContext:
    """Build a verifying TLS context that trusts only certifi's Mozilla CA bundle."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    return ctx


def fetch(url: str, timeout: float = 10.0) -> tuple[int, bytes]:
    ctx = make_ssl_context()
    with urllib.request.urlopen(url, context=ctx, timeout=timeout) as resp:
        return resp.status, resp.read()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default="https://www.python.org")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    print(f"CA bundle: {certifi.where()} (certifi {certifi.__version__})")
    try:
        status, body = fetch(args.url, args.timeout)
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLCertVerificationError):
            sys.exit(f"Certificate verification failed: {e.reason.verify_message}")
        sys.exit(f"Request failed: {e.reason}")
    except OSError as e:
        sys.exit(f"Request failed: {e}")
    print(f"{args.url} -> HTTP {status}, {len(body)} bytes, certificate verified")
