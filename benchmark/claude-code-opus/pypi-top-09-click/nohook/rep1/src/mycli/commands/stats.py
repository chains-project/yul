"""``mycli stats``: count lines, words, and characters in files."""

from __future__ import annotations

import argparse
import json
import logging
import sys

log = logging.getLogger(__name__)

FIELDS = ("lines", "words", "chars")


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("stats", help="count lines/words/chars in files", description=__doc__)
    parser.add_argument(
        "files", nargs="*", type=argparse.FileType("r", encoding="utf-8"), default=[sys.stdin],
        help="files to read (default: stdin; use - for stdin)",
    )
    parser.add_argument(
        "-f", "--format", choices=("text", "json"), default="text", help="output format (default: %(default)s)",
    )
    parser.add_argument(
        "--only", choices=FIELDS, action="append", help="restrict output to a field (repeatable)",
    )
    parser.set_defaults(func=run)


def count(text: str) -> dict[str, int]:
    return {"lines": text.count("\n"), "words": len(text.split()), "chars": len(text)}


def run(args: argparse.Namespace) -> int:
    fields = args.only or list(FIELDS)
    results = []
    for f in args.files:
        log.info("reading %s", f.name)
        with f:
            counts = count(f.read())
        results.append({"file": f.name, **{k: counts[k] for k in fields}})

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        for row in results:
            print("\t".join(str(row[k]) for k in fields) + f"\t{row['file']}")
    return 0
