"""Command-line interface for :mod:`idnatool`."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .core import IDNAError, Profile, decode, encode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idnatool",
        description="Encode and decode internationalized domain names (IDNA2008 / UTS #46).",
    )
    parser.add_argument(
        "command",
        choices=("encode", "decode"),
        help="encode: Unicode -> A-label (punycode); decode: A-label -> Unicode",
    )
    parser.add_argument("domain", nargs="+", help="domain name(s) to process")
    parser.add_argument(
        "-p",
        "--profile",
        choices=[p.value for p in Profile],
        default=Profile.IDNA2008.value,
        help="UTS #46 processing profile (default: strict)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    profile = Profile(args.profile)
    fn = encode if args.command == "encode" else decode

    status = 0
    for domain in args.domain:
        try:
            print(fn(domain, profile=profile))
        except IDNAError as exc:
            print(f"idnatool: {domain}: {exc}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
