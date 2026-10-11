"""Command-line entry point for secure-fetch."""

from __future__ import annotations

import argparse
import sys

from . import ca_bundle_path, fetch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="secure-fetch",
        description="Fetch an HTTPS URL using the certifi CA bundle.",
    )
    parser.add_argument("url", nargs="?", help="HTTPS URL to fetch")
    parser.add_argument(
        "--show-ca-bundle",
        action="store_true",
        help="print the path to the CA bundle and exit",
    )
    args = parser.parse_args(argv)

    if args.show_ca_bundle:
        print(ca_bundle_path())
        return 0

    if not args.url:
        parser.error("the following arguments are required: url")

    try:
        sys.stdout.buffer.write(fetch(args.url))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
