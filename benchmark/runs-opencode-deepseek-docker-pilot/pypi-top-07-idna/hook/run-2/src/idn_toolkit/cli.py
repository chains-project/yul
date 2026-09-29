"""Command line interface for :mod:`idn_toolkit`."""

from __future__ import annotations

import argparse
import sys

from . import core


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idn",
        description="Encode and decode internationalized domain names.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("encode", "Unicode domain -> ASCII/punycode (xn--)"),
        ("decode", "ASCII/punycode (xn--) -> Unicode domain"),
    ):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("domains", nargs="+", help="domain name(s) to process")
        sub.add_argument(
            "--uts46",
            action="store_true",
            help="apply UTS #46 mapping before processing",
        )
        sub.add_argument(
            "--std3",
            action="store_true",
            help="enforce STD3 ASCII rules",
        )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    operation = core.encode if args.command == "encode" else core.decode

    status = 0
    for domain in args.domains:
        try:
            print(operation(domain, uts46=args.uts46, std3_rules=args.std3))
        except core.IDNAError as exc:
            print(f"idn: {domain!r}: {exc}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
