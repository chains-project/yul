"""Command-line interface: ``idnconv encode|decode DOMAIN...``."""

import argparse
import sys

from idnconv.core import IDNAError, decode, encode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="idnconv",
        description="Encode/decode internationalized domain names (IDNA 2008).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="Unicode -> ASCII (xn--) form")
    enc.add_argument("domains", nargs="+", metavar="DOMAIN")
    enc.add_argument(
        "--strict",
        action="store_true",
        help="disable UTS #46 mapping (input must already be normalized)",
    )

    dec = sub.add_parser("decode", help="ASCII (xn--) -> Unicode form")
    dec.add_argument("domains", nargs="+", metavar="DOMAIN")

    args = parser.parse_args(argv)

    status = 0
    for domain in args.domains:
        try:
            if args.command == "encode":
                print(encode(domain, uts46=not args.strict))
            else:
                print(decode(domain))
        except IDNAError as exc:
            print(f"idnconv: {domain!r}: {exc}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
