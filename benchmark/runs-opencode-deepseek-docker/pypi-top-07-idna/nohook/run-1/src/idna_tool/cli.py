"""Command line interface for :mod:`idna_tool`."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from . import __version__
from .core import IDNAError, decode, encode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode and decode internationalized domain names.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    encoder = subparsers.add_parser(
        "encode", help="convert a Unicode domain to its ASCII (punycode) form"
    )
    encoder.add_argument("domain", help="domain name to encode")

    decoder = subparsers.add_parser(
        "decode", help="convert an ASCII (punycode) domain to Unicode"
    )
    decoder.add_argument("domain", help="domain name to decode")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "encode":
            print(encode(args.domain))
        else:
            print(decode(args.domain))
    except IDNAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
