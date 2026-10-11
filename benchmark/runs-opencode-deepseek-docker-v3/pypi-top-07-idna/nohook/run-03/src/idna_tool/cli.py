"""Command line interface for idna-tool."""

from __future__ import annotations

import argparse
import sys

import idna

from .core import decode, encode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode and decode internationalized domain names (IDNA).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser(
        "encode", help="Unicode domain -> ASCII (A-label)"
    )
    encode_parser.add_argument("domain")

    decode_parser = subparsers.add_parser(
        "decode", help="ASCII domain -> Unicode"
    )
    decode_parser.add_argument("domain")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "encode":
            print(encode(args.domain))
        else:
            print(decode(args.domain))
    except idna.IDNAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
