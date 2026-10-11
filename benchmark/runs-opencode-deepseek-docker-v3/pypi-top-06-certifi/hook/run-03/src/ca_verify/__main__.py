"""Command line entry point for ``ca-verify``."""

from __future__ import annotations

import argparse
import sys
import urllib.request
from typing import List, Optional

from . import ca_bundle_path, ssl_context


def verify(url: str, timeout: float = 15.0) -> int:
    """Fetch ``url`` over HTTPS using the bundled roots.

    Returns 0 on success and 1 on any verification or connection failure.
    """
    try:
        with urllib.request.urlopen(
            url, context=ssl_context(), timeout=timeout
        ) as response:
            print(f"OK {response.status} {url}")
            return 0
    except Exception as exc:  # noqa: BLE001 - report any verification failure
        print(f"FAIL {url}: {exc}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ca-verify",
        description="Verify HTTPS endpoints against an up-to-date root CA bundle.",
    )
    parser.add_argument("url", nargs="?", help="HTTPS URL to verify.")
    parser.add_argument(
        "--path",
        action="store_true",
        help="Print the path to the CA bundle and exit.",
    )
    args = parser.parse_args(argv)

    if args.path or not args.url:
        print(ca_bundle_path())

    if args.url:
        return verify(args.url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
