"""Command-line entry point for fetching a URL with a resilient session."""

from __future__ import annotations

import argparse
import sys

from .session import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, build_session


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="resilient-http",
        description="Fetch a URL using connection pooling and automatic retries.",
    )
    parser.add_argument("url", help="URL to request")
    parser.add_argument(
        "-X",
        "--method",
        default="GET",
        help="HTTP method to use (default: GET)",
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"maximum retry attempts (default: {DEFAULT_MAX_RETRIES})",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"per-request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    with build_session(max_retries=args.retries) as session:
        response = session.request(args.method, args.url, timeout=args.timeout)
        response.raise_for_status()

    print(f"{response.status_code} {response.reason}")
    print(response.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
