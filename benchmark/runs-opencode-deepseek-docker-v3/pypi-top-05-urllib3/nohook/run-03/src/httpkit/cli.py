"""Command-line entry point for quick one-off requests."""

from __future__ import annotations

import argparse
import sys

from .client import HTTPClient, HTTPError, RetryPolicy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="httpkit",
        description="Fetch a URL using pooled connections with automatic retries.",
    )
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("-H", "--header", action="append", default=[], metavar="K:V")
    parser.add_argument("-d", "--data", default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--maxsize", type=int, default=10)
    parser.add_argument("--backoff", type=float, default=0.5)
    parser.add_argument("--stream", action="store_true")
    return parser


def _parse_headers(items: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in items:
        if ":" not in item:
            raise SystemExit(f"invalid header {item!r}, expected 'Key: Value'")
        key, value = item.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy = RetryPolicy(total=args.retries, backoff_factor=args.backoff)

    try:
        with HTTPClient(
            timeout=args.timeout,
            retries=policy,
            maxsize=args.maxsize,
            headers=_parse_headers(args.header),
        ) as client:
            if args.stream:
                for chunk in client.stream(args.method, args.url, body=args.data):
                    sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
            else:
                response = client.request(
                    args.method,
                    args.url,
                    body=args.data,
                    preload_content=True,
                )
                sys.stdout.buffer.write(response.data)
    except HTTPError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
