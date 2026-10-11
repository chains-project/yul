from __future__ import annotations

import argparse
import json
import sys

from .client import ApiError, fetch_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="api-fetcher",
        description="Fetch JSON data from a REST API over HTTP.",
    )
    parser.add_argument("url", help="API endpoint to fetch")
    parser.add_argument(
        "-o",
        "--output",
        help="write the response to this file instead of stdout",
    )
    args = parser.parse_args(argv)

    try:
        data = fetch_json(args.url)
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
