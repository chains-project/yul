"""CLI entry point for the api-fetcher script."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from .api_client import APIClient

log = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch data from a REST API and output it as JSON.",
    )
    parser.add_argument(
        "url",
        help="Base URL of the API (e.g. https://api.example.com)",
    )
    parser.add_argument(
        "endpoint",
        nargs="?",
        default="",
        help="API endpoint path (e.g. /v1/users). Defaults to root.",
    )
    parser.add_argument(
        "--header",
        "-H",
        action="append",
        metavar="KEY:VALUE",
        dest="headers",
        help="Extra HTTP header (can be repeated).",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=10.0,
        help="Request timeout in seconds (default: 10).",
    )
    parser.add_argument(
        "--method",
        "-X",
        choices=["GET", "POST"],
        default="GET",
        help="HTTP method to use (default: GET).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="-",
        help="Output file path. Default: stdout.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    headers: dict[str, str] = {}
    for h in (args.headers or []):
        key, _, value = h.partition(":")
        headers[key.strip()] = value.strip()

    with APIClient(
        base_url=args.url,
        timeout=args.timeout,
        headers=headers,
    ) as client:
        if args.method == "POST":
            result = client.post(args.endpoint)
        else:
            result = client.get(args.endpoint)

    output = json.dumps(result, indent=2, default=str)

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w") as f:
            f.write(output)
        log.info("Output written to %s", args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())