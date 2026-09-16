#!/usr/bin/env python3
"""Script that uses certifi for reliable SSL/TLS certificate verification."""

import sys
import ssl
import urllib.request
import certifi


def verify_https(url):
    """Verify an HTTPS connection using certifi's root certificates."""
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=context) as response:
        return response.read()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.python.org/"
    print(f"CA bundle path: {certifi.where()}")
    print(f"Fetching {url}...")
    data = verify_https(url)
    print(f"Successfully fetched {len(data)} bytes")