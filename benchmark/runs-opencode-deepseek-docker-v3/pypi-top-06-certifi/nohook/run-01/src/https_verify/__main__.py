from __future__ import annotations

import argparse
import ssl
import sys

from .client import ca_bundle_path, fetch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="https-verify",
        description="Fetch a URL over HTTPS, verifying it against certifi's root CA bundle.",
    )
    parser.add_argument("url", nargs="?", help="HTTPS URL to fetch")
    parser.add_argument(
        "--show-ca-bundle",
        action="store_true",
        help="print the path to the CA bundle used for verification and exit",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=30.0,
        help="request timeout in seconds (default: 30)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.show_ca_bundle:
        print(ca_bundle_path())
        return 0

    if not args.url:
        build_parser().error("a URL is required unless --show-ca-bundle is used")

    try:
        body = fetch(args.url, timeout=args.timeout)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ssl.SSLCertVerificationError as exc:
        print(f"TLS verification failed: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1

    print(f"OK: {args.url} verified with {ca_bundle_path()}")
    print(f"received {len(body)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
