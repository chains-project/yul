"""Command-line interface for IDNA encoding and decoding."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import IDNError, decode, encode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idn",
        description="Encode and decode internationalized domain names (IDNA2008).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("domain", nargs="?", help="domain name; reads stdin if omitted")
    common.add_argument("--uts46", action="store_true", help="apply UTS #46 mapping")
    common.add_argument(
        "--transitional",
        action="store_true",
        help="use transitional processing (only with --uts46)",
    )
    common.add_argument(
        "--std3-rules", action="store_true", help="enforce STD3 ASCII rules"
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("encode", parents=[common], help="Unicode -> ASCII (A-label)")
    sub.add_parser("decode", parents=[common], help="ASCII (A-label) -> Unicode")
    return parser


def _read_domain(args: argparse.Namespace) -> str:
    if args.domain is not None:
        return args.domain
    return sys.stdin.read().strip()


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "encode":
            result = encode(
                _read_domain(args),
                uts46=args.uts46,
                std3_rules=args.std3_rules,
                transitional=args.transitional,
            )
        else:
            result = decode(
                _read_domain(args),
                uts46=args.uts46,
                std3_rules=args.std3_rules,
            )
    except (IDNError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
