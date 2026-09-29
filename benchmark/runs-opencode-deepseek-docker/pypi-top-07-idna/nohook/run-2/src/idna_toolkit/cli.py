"""Command line interface for :mod:`idna_toolkit`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence

from .core import IDNAError, decode, encode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idna-toolkit",
        description="Encode and decode internationalized domain names (IDNA 2008).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser(
        "encode", help="Encode Unicode domain names to ASCII (A-labels)."
    )
    decode_parser = subparsers.add_parser(
        "decode", help="Decode ASCII domain names to Unicode."
    )

    for sub in (encode_parser, decode_parser):
        sub.add_argument(
            "domains",
            nargs="*",
            help="Domain names to process. Reads newline separated names from stdin when omitted.",
        )
        sub.add_argument(
            "--uts46",
            action="store_true",
            help="Apply UTS #46 processing (useful for user supplied input).",
        )
        sub.add_argument(
            "--display",
            action="store_true",
            help="Best-effort decoding for display (decode only).",
        )

    encode_parser.add_argument(
        "--transitional",
        action="store_true",
        help="Use transitional UTS #46 processing (requires --uts46).",
    )
    return parser


def _read_domains(domains: Sequence[str]) -> Iterable[str]:
    if domains:
        yield from domains
        return
    for line in sys.stdin:
        line = line.strip()
        if line:
            yield line


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``idna-toolkit`` command."""
    args = _build_parser().parse_args(argv)
    status = 0
    for domain in _read_domains(args.domains):
        try:
            if args.command == "encode":
                result = encode(
                    domain,
                    uts46=args.uts46,
                    transitional=args.transitional,
                )
            else:
                result = decode(
                    domain,
                    uts46=args.uts46,
                    display=args.display,
                )
        except IDNAError as exc:
            status = 1
            print(f"{domain}: error: {exc}", file=sys.stderr)
            continue
        print(result)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
