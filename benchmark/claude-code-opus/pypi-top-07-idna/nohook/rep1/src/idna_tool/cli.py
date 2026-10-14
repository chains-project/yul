"""Command-line interface for IDNA encoding and decoding."""

import argparse
import sys

import idna

from idna_tool.codec import decode, encode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode/decode internationalized domain names (IDNA 2008).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="Unicode -> ASCII (Punycode)")
    enc.add_argument("domains", nargs="+")
    enc.add_argument("--strict", action="store_true",
                     help="disable UTS #46 mapping (input must already be normalized)")

    dec = sub.add_parser("decode", help="ASCII (Punycode) -> Unicode")
    dec.add_argument("domains", nargs="+")

    args = parser.parse_args(argv)
    status = 0
    for domain in args.domains:
        try:
            if args.command == "encode":
                print(encode(domain, uts46=not args.strict))
            else:
                print(decode(domain))
        except idna.IDNAError as exc:
            print(f"error: {domain!r}: {exc}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
