from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional

from .client import ApiClient, ApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fetch-api",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="endpoint URL, or a path relative to --base-url")
    parser.add_argument(
        "-b",
        "--base-url",
        default="",
        help="base URL used when URL is a relative path",
    )
    parser.add_argument(
        "-p",
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="query parameter (repeatable)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        metavar="NAME: VALUE",
        help="request header (repeatable)",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="retry attempts for failed GETs")
    return parser


def _parse_pairs(items: List[str], separator: str, flag: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition(separator)
        if not sep or not key.strip():
            raise SystemExit(f"error: invalid {flag} value {item!r}, expected KEY{separator.strip()}VALUE")
        pairs[key.strip()] = value.strip()
    return pairs


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    params = _parse_pairs(args.param, "=", "--param")
    headers = _parse_pairs(args.header, ":", "--header")

    try:
        with ApiClient(
            args.base_url,
            timeout=args.timeout,
            retries=args.retries,
            headers=headers,
        ) as client:
            data = client.get_json(args.url, params=params)
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
