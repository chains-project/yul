"""Command line interface for :mod:`idn_tools`."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from idn_tools.core import IDNAError, decode_domain, encode_domain


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idn",
        description="Encode and decode internationalized domain names (IDNA 2008 / UTS #46).",
    )
    parser.add_argument(
        "--no-uts46",
        action="store_true",
        help="disable UTS #46 mapping (use strict IDNA 2008 rules)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="convert a Unicode domain to ASCII (A-label)")
    enc.add_argument("domains", nargs="+", help="domain name(s) to encode")

    dec = sub.add_parser("decode", help="convert an ASCII domain to Unicode (U-label)")
    dec.add_argument("domains", nargs="+", help="domain name(s) to decode")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    uts46 = not args.no_uts46

    convert = encode_domain if args.command == "encode" else decode_domain

    status = 0
    for domain in args.domains:
        try:
            print(convert(domain, uts46=uts46))
        except (IDNAError, UnicodeError) as exc:
            print(f"{domain}: {exc}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
