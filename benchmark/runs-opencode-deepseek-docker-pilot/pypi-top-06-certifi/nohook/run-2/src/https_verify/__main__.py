"""Command-line entry point: verify and fetch an HTTPS URL."""

from __future__ import annotations

import argparse
import sys

from .ca_bundle import ca_bundle_path, create_ssl_context
from .fetch import fetch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="https-verify", description=__doc__)
    parser.add_argument("url", nargs="?", help="HTTPS URL to verify and fetch")
    parser.add_argument(
        "--show-bundle",
        action="store_true",
        help="print the path to the CA bundle and exit",
    )
    args = parser.parse_args(argv)

    if args.show_bundle or not args.url:
        print(ca_bundle_path())
        return 0

    context = create_ssl_context()
    try:
        body = fetch(args.url, context=context)
    except Exception as exc:  # noqa: BLE001 - report any failure to the user
        print(f"FAILED: {args.url}: {exc}", file=sys.stderr)
        return 1

    print(f"OK: verified {args.url} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
