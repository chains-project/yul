import argparse

import idna


def encode(domain: str) -> str:
    return idna.encode(domain).decode("ascii")


def decode(domain: str) -> str:
    return idna.decode(domain)


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode/decode IDNA domain names")
    sub = parser.add_subparsers(dest="command", required=True)

    encode_p = sub.add_parser("encode", help="Convert a Unicode domain to A-label (punycode)")
    encode_p.add_argument("domain")

    decode_p = sub.add_parser("decode", help="Convert an A-label domain back to Unicode")
    decode_p.add_argument("domain")

    args = parser.parse_args()

    if args.command == "encode":
        print(encode(args.domain))
    else:
        print(decode(args.domain))


if __name__ == "__main__":
    main()
