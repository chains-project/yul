"""Encode and decode internationalized domain names per IDNA 2008 (RFC 5891).

Uses the ``idna`` package rather than Python's built-in ``"idna"`` codec,
which only implements the obsolete IDNA 2003 standard.
"""

import argparse
import sys

import idna


def encode(domain: str, uts46: bool = True) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode "xn--") form.

    With ``uts46`` enabled (the default), the input is first normalized per
    UTS #46 (e.g. case-folded), matching how browsers handle user input.
    """
    return idna.encode(domain, uts46=uts46).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII (Punycode "xn--") domain name to its Unicode form."""
    return idna.decode(domain)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode or decode internationalized domain names (IDNA 2008).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="Unicode -> ASCII (xn--)")
    enc.add_argument("domains", nargs="+")
    enc.add_argument(
        "--strict",
        action="store_true",
        help="disable UTS #46 mapping; reject input that is not already canonical",
    )

    dec = sub.add_parser("decode", help="ASCII (xn--) -> Unicode")
    dec.add_argument("domains", nargs="+")

    args = parser.parse_args(argv)

    status = 0
    for domain in args.domains:
        try:
            if args.command == "encode":
                print(encode(domain, uts46=not args.strict))
            else:
                print(decode(domain))
        except idna.IDNAError as e:
            print(f"idna-tool: {domain!r}: {e}", file=sys.stderr)
            status = 1
    return status


def cli() -> None:
    sys.exit(main())
