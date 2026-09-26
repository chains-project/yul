import sys

import requests

API_URL = "https://jsonplaceholder.typicode.com/posts/1"


def fetch(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else API_URL
    data = fetch(url)
    print(data)


if __name__ == "__main__":
    main()
