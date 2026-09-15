"""Verify an HTTPS connection using certifi's root CA bundle."""

import ssl
import urllib.request

import certifi


def fetch(url: str) -> bytes:
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=context) as response:
        return response.read()


if __name__ == "__main__":
    body = fetch("https://www.python.org")
    print(f"Fetched {len(body)} bytes using CA bundle: {certifi.where()}")
