"""Encode and decode internationalized domain names (IDNA)."""

import sys

import idna


def encode(domain: str) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode) form."""
    return idna.encode(domain).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII (Punycode) domain name back to Unicode."""
    return idna.decode(domain)


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in ("encode", "decode"):
        print(f"usage: {sys.argv[0]} <encode|decode> <domain>", file=sys.stderr)
        sys.exit(1)

    action, domain = sys.argv[1], sys.argv[2]
    result = encode(domain) if action == "encode" else decode(domain)
    print(result)


if __name__ == "__main__":
    main()
