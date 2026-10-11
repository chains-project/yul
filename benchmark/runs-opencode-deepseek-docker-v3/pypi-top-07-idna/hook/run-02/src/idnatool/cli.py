"""Command line interface for the ``idna-tool`` script."""

from __future__ import annotations

import argparse
import sys

from .core import IDNAError, decode_domain, encode_domain


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idna-tool",
        description="Encode and decode internationalized domain names (IDNA 2008 / UTS #46).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(sub: argparse.ArgumentParser) -> None:
        sub.add_argument(
            "domain",
            nargs="*",
            help="domain name(s); read from stdin when omitted",
        )
        sub.add_argument(
            "--no-uts46",
            dest="uts46",
            action="store_false",
            help="disable UTS #46 mapping/normalization",
        )
        sub.add_argument(
            "--strict",
            action="store_true",
            help="disallow deviations from the specification",
        )
        sub.add_argument(
            "--std3-rules",
            action="store_true",
            help="enforce STD3 ASCII rules",
        )

    encode = subparsers.add_parser("encode", help="convert Unicode domain to ASCII (A-label)")
    add_common(encode)

    decode = subparsers.add_parser("decode", help="convert ASCII domain (A-label) to Unicode")
    add_common(decode)

    return parser


def _iter_domains(args: argparse.Namespace):
    if args.domain:
        yield from args.domain
        return
    for line in sys.stdin:
        line = line.strip()
        if line:
            yield line


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    common = {
        "uts46": args.uts46,
        "strict": args.strict,
        "std3_rules": args.std3_rules,
    }

    status = 0
    for domain in _iter_domains(args):
        try:
            if args.command == "encode":
                result = encode_domain(domain, **common)
            else:
                result = decode_domain(domain, **common)
        except IDNAError as exc:
            print(f"idna-tool: {domain!r}: {exc}", file=sys.stderr)
            status = 1
            continue
        print(result)

    return status


if __name__ == "__main__":
    raise SystemExit(main())
