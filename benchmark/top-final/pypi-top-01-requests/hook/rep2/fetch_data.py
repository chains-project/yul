import sys

import requests

API_URL = "https://api.github.com/repos/psf/requests"


def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    try:
        data = fetch_data(API_URL)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(data)


if __name__ == "__main__":
    main()
