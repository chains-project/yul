import sys

import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"


def fetch_data(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else API_URL
    data = fetch_data(url)
    print(data)


if __name__ == "__main__":
    main()
