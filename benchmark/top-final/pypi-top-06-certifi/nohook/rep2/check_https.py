import ssl
import sys
import urllib.request

import certifi


def verify(url: str) -> None:
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=context) as response:
        print(f"{url} -> HTTP {response.status}, certificate verified OK")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    verify(target)
