"""``mytool stats``: file arguments (including stdin) and output formats."""

from __future__ import annotations

import argparse
import json
import sys

from mytool.errors import CLIError


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "stats", help="count lines, words, and characters in files"
    )
    p.add_argument(
        "files", nargs="*", default=["-"], metavar="FILE",
        help="files to read ('-' or omitted for stdin)",
    )
    p.add_argument(
        "-f", "--format", choices=("text", "json"), default="text",
        help="output format (default: %(default)s)",
    )
    p.set_defaults(func=run)


def count(text: str) -> dict[str, int]:
    return {
        "lines": text.count("\n"),
        "words": len(text.split()),
        "chars": len(text),
    }


def read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        raise CLIError(f"cannot read {path}: {exc.strerror}") from exc


def run(args: argparse.Namespace) -> int:
    results = [{"file": path, **count(read(path))} for path in args.files]

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['lines']:>8} {r['words']:>8} {r['chars']:>8} {r['file']}")
    return 0
