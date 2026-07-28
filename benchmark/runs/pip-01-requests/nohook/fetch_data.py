import sys

import requests

API_URL = "https://api.github.com/repos/psf/requests"


def fetch(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else API_URL
    data = fetch(url)
    print(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
