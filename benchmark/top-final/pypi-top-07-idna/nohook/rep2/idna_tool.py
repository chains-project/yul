import argparse
import sys

import idna


def encode(domain: str) -> str:
    return idna.encode(domain).decode("ascii")


def decode(domain: str) -> str:
    return idna.decode(domain)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode a Unicode domain to A-label (punycode)")
    encode_parser.add_argument("domain")

    decode_parser = subparsers.add_parser("decode", help="Decode an A-label domain to Unicode")
    decode_parser.add_argument("domain")

    args = parser.parse_args()

    try:
        if args.command == "encode":
            print(encode(args.domain))
        else:
            print(decode(args.domain))
    except idna.IDNAError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
