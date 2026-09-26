import ssl
import sys
import urllib.request

import certifi


def check_https(url: str) -> None:
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=context) as response:
        print(f"{url} -> HTTP {response.status}, verified against {certifi.where()}")


if __name__ == "__main__":
    check_https(sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com")
