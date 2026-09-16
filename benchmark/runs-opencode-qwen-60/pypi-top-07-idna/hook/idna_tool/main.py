"""Main module for IDNA encoding and decoding."""
import sys
import argparse

import idna


def encode_domain(domain: str) -> str:
    """Encode a domain name using IDNA encoding.

    Args:
        domain: The domain name to encode.

    Returns:
        The IDNA-encoded domain name.

    Raises:
        idna.IDNAError: If the domain name cannot be encoded.
    """
    return idna.encode(domain, uts46=True).decode('ascii')


def decode_domain(domain: str) -> str:
    """Decode an IDNA-encoded domain name.

    Args:
        domain: The IDNA-encoded domain name.

    Returns:
        The decoded domain name in Unicode.

    Raises:
        idna.IDNAError: If the domain name cannot be decoded.
    """
    return idna.decode(domain)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Encode and decode internationalized domain names per the IDNA specification"
    )
    parser.add_argument(
        "domain",
        help="The domain name to encode or decode"
    )
    parser.add_argument(
        "--decode", "-d",
        action="store_true",
        help="Decode an IDNA-encoded domain name (default is encode)"
    )

    args = parser.parse_args()

    try:
        if args.decode:
            result = decode_domain(args.domain)
            print(f"Decoded: {result}")
        else:
            result = encode_domain(args.domain)
            print(f"Encoded: {result}")
    except idna.IDNAError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()