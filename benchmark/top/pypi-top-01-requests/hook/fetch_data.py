import sys

import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"


def fetch_data(url: str) -> list:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    try:
        data = fetch_data(API_URL)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(data)} items from {API_URL}")
    for item in data[:5]:
        print(item)


if __name__ == "__main__":
    main()
