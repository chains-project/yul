import argparse

import idna


def encode(domain: str) -> str:
    return idna.encode(domain).decode("ascii")


def decode(domain: str) -> str:
    return idna.decode(domain)


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode/decode internationalized domain names (IDNA)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode a Unicode domain to A-label (punycode) form")
    encode_parser.add_argument("domain")

    decode_parser = subparsers.add_parser("decode", help="Decode an A-label (punycode) domain to Unicode form")
    decode_parser.add_argument("domain")

    args = parser.parse_args()

    if args.command == "encode":
        print(encode(args.domain))
    elif args.command == "decode":
        print(decode(args.domain))


if __name__ == "__main__":
    main()
