from __future__ import annotations

import argparse
import sys

from urllib3.exceptions import HTTPError

from http_script.client import HttpClient, build_retry


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal pooled HTTP client.")
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET", help="HTTP method")
    parser.add_argument("-H", "--header", action="append", default=[], metavar="NAME:VALUE")
    parser.add_argument("--retries", type=int, default=5, help="Total retry attempts")
    parser.add_argument("--backoff", type=float, default=0.5, help="Retry backoff factor")
    parser.add_argument("--timeout", type=float, default=10.0, help="Connect/read timeout")
    parser.add_argument("--max-connections", type=int, default=10, help="Connections per host")
    return parser.parse_args(argv)


def parse_headers(values: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for value in values:
        name, sep, header_value = value.partition(":")
        if not sep:
            raise SystemExit(f"invalid header {value!r}; expected NAME:VALUE")
        headers[name.strip()] = header_value.strip()
    return headers


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    retries = build_retry(total=args.retries, backoff_factor=args.backoff)
    try:
        with HttpClient(
            maxsize=args.max_connections,
            timeout=args.timeout,
            retries=retries,
            headers=parse_headers(args.header),
        ) as client:
            response = client.request(args.method, args.url)
            sys.stdout.write(response.data.decode("utf-8", errors="replace"))
    except HTTPError as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
