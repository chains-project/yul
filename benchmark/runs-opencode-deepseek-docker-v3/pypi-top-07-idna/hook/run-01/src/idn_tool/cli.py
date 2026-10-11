"""Command line interface for :mod:`idn_tool`."""

from __future__ import annotations

import argparse
import sys

from .core import IDNError, decode, encode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idn-tool",
        description="Encode and decode internationalized domain names (IDNA).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser(
        "encode", help="convert a domain to its ASCII (A-label) form"
    )
    encode_parser.add_argument(
        "domains", nargs="+", metavar="DOMAIN", help="domain name(s) to encode"
    )
    encode_parser.add_argument(
        "--uts46",
        action="store_true",
        help="apply UTS #46 processing (case folding, compatibility mapping)",
    )
    encode_parser.add_argument(
        "--std3-rules",
        action="store_true",
        help="enforce the STD3 ASCII rules",
    )

    decode_parser = subparsers.add_parser(
        "decode", help="convert a domain to its Unicode (U-label) form"
    )
    decode_parser.add_argument(
        "domains", nargs="+", metavar="DOMAIN", help="domain name(s) to decode"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``idn-tool`` command."""
    args = _build_parser().parse_args(argv)
    status = 0

    for domain in args.domains:
        try:
            if args.command == "encode":
                result = encode(domain, uts46=args.uts46, std3_rules=args.std3_rules)
            else:
                result = decode(domain)
        except IDNError as exc:
            print(f"{domain}: error: {exc}", file=sys.stderr)
            status = 1
            continue
        print(result)

    return status


if __name__ == "__main__":
    raise SystemExit(main())
