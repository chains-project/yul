import sys

import requests

API_URL = "https://jsonplaceholder.typicode.com/posts/1"


def fetch(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> int:
    try:
        data = fetch(API_URL)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    print(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
