import ssl
import sys
import urllib.request

import certifi


def fetch(url: str) -> bytes:
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=context) as response:
        return response.read()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    body = fetch(target)
    print(f"Fetched {len(body)} bytes from {target} using certifi {certifi.__version__ if hasattr(certifi, '__version__') else certifi.where()}")
