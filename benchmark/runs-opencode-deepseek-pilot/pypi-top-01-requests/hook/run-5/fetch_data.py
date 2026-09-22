"""Fetch data from a REST API over HTTP.

Example:
    python fetch_data.py https://jsonplaceholder.typicode.com/todos/1
"""

from __future__ import annotations

import argparse
import json
import sys

import requests

DEFAULT_URL = "https://jsonplaceholder.typicode.com/todos/1"
DEFAULT_TIMEOUT = 10.0


def fetch_json(url: str, *, params: dict | None = None, timeout: float = DEFAULT_TIMEOUT):
    """GET ``url`` and return the decoded JSON body.

    Raises ``requests.HTTPError`` for non-2xx responses and
    ``requests.RequestException`` for connection/timeout failures.
    """
    response = requests.get(
        url,
        params=params,
        timeout=timeout,
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch JSON data from a REST API.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="endpoint to GET")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="request timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="write the response body to this file instead of stdout",
    )
    args = parser.parse_args(argv)

    try:
        data = fetch_json(args.url, timeout=args.timeout)
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    body = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(body + "\n")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
