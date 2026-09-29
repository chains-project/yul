"""Command-line interface for IDNA encoding and decoding."""

from __future__ import annotations

import argparse
import sys

from idn_tool.core import IDNAError, decode, to_ascii


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idn-tool",
        description="Encode and decode internationalized domain names (IDNA).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="Encode a Unicode domain to ASCII (A-label).")
    enc.add_argument("domain", help="Unicode domain name, e.g. b'bücher.example'")
    enc.add_argument(
        "--uts46",
        action="store_true",
        help="Apply UTS #46 processing (maps and normalizes input).",
    )
    enc.add_argument(
        "--strict",
        action="store_true",
        help="Fail on deviations instead of mapping them.",
    )

    dec = sub.add_parser("decode", help="Decode an ASCII domain to Unicode (U-label).")
    dec.add_argument("domain", help="ASCII domain name, e.g. xn--bcher-kva.example")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "encode":
            print(to_ascii(args.domain, uts46=args.uts46, strict=args.strict))
        else:
            print(decode(args.domain))
    except IDNAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
