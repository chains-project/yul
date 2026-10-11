"""Command-line interface for idna-tool."""

from __future__ import annotations

import argparse
import sys

from . import IDNAError, decode, encode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode and decode internationalized domain names (IDNA).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("encode", "convert a Unicode domain to its ASCII (A-label) form"),
        ("decode", "convert an ASCII domain to its Unicode (U-label) form"),
    ):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("domain", help="domain name to convert")
        sub.add_argument(
            "--uts46",
            action="store_true",
            help="apply UTS #46 processing",
        )
        sub.add_argument(
            "--std3-rules",
            action="store_true",
            help="enforce STD3 ASCII rules",
        )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "encode":
            result = encode(
                args.domain,
                uts46=args.uts46,
                std3_rules=args.std3_rules,
            )
        else:
            result = decode(
                args.domain,
                uts46=args.uts46,
                std3_rules=args.std3_rules,
            )
    except IDNAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
