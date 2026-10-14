"""Fetch a URL over HTTPS, verifying the server against certifi's CA bundle."""

import argparse
import ssl
import sys
import urllib.error
import urllib.request

import certifi


def make_ssl_context() -> ssl.SSLContext:
    """Return a context with hostname checking and certifi's root CAs."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, timeout: float = 10.0) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout, context=make_ssl_context()) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="HTTPS URL to fetch")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    if not args.url.lower().startswith("https://"):
        parser.error("only https:// URLs are supported")

    try:
        body = fetch(args.url, args.timeout)
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLCertVerificationError):
            print(f"Certificate verification failed: {e.reason.verify_message}", file=sys.stderr)
        else:
            print(f"Request failed: {e.reason}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1

    sys.stdout.buffer.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
