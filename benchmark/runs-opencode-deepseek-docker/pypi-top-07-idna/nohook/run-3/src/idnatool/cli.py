"""Command-line interface for :mod:`idnatool`."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .core import Codec, IDNAError


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "domain",
        nargs="?",
        help="domain name to process; read from stdin when omitted",
    )
    parser.add_argument(
        "--no-uts46",
        dest="uts46",
        action="store_false",
        help="disable UTS #46 mapping/normalization",
    )
    parser.add_argument(
        "--std3-rules",
        action="store_true",
        help="enforce STD3 ASCII rules",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode and decode internationalized domain names (IDNA 2008).",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    encode_parser = subcommands.add_parser(
        "encode", help="Unicode domain -> ASCII (A-label) form"
    )
    _add_common_options(encode_parser)

    decode_parser = subcommands.add_parser(
        "decode", help="ASCII (A-label) domain -> Unicode"
    )
    _add_common_options(decode_parser)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    domain = args.domain
    if domain is None:
        domain = sys.stdin.read().strip()

    codec = Codec(uts46=args.uts46, std3_rules=args.std3_rules)
    try:
        if args.command == "encode":
            result = codec.encode(domain)
        else:
            result = codec.decode(domain)
    except IDNAError as exc:
        print(f"idna-tool: error: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
