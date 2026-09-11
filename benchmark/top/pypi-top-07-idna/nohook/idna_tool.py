"""Encode and decode internationalized domain names per RFC 5891 (IDNA)."""

import argparse
import sys

import idna


def encode_domain(domain: str) -> str:
    return idna.encode(domain).decode("ascii")


def decode_domain(domain: str) -> str:
    return idna.decode(domain)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    encode_parser = sub.add_parser("encode", help="Encode a Unicode domain to A-label (punycode) form")
    encode_parser.add_argument("domain")

    decode_parser = sub.add_parser("decode", help="Decode an A-label (punycode) domain to Unicode")
    decode_parser.add_argument("domain")

    args = parser.parse_args()

    try:
        if args.command == "encode":
            print(encode_domain(args.domain))
        else:
            print(decode_domain(args.domain))
    except idna.IDNAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
