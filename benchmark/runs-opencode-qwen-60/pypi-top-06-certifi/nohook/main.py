#!/usr/bin/env python3
"""Verify HTTPS connections using certifi's up-to-date root certificates."""

import json
import urllib.request
import certifi

def main():
    # certifi.where() returns the path to the bundled root CA bundle
    ca_path = certifi.where()
    print(f"Using CA bundle: {ca_path}")

    # Verify an HTTPS request with the certifi bundle
    ctx = urllib.request.build_opener(
        urllib.request.HTTPSHandler(
            context=__import__("ssl").create_default_context(cafile=ca_path)
        )
    )

    with ctx.open("https://www.googleapis.com") as response:
        data = response.read().decode("utf-8")

    result = json.loads(data)
    print(f"HTTPS verified successfully — {result.get('name', 'unknown')}")

if __name__ == "__main__":
    main()