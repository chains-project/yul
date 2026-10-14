"""Count lines, words, and characters in files (or stdin)."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass

from mycli.errors import CLIError

log = logging.getLogger(__name__)

FIELDS = ("lines", "words", "chars")


@dataclass
class Counts:
    name: str
    lines: int
    words: int
    chars: int


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "count", help="count lines, words, and characters", description=__doc__
    )
    parser.add_argument(
        "files", nargs="*", metavar="FILE", help="files to read ('-' or none for stdin)"
    )
    parser.add_argument("-l", "--lines", action="store_true", help="show line counts")
    parser.add_argument("-w", "--words", action="store_true", help="show word counts")
    parser.add_argument("-c", "--chars", action="store_true", help="show character counts")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="output format (default: text)"
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    # With no field flags, show everything (like `wc`).
    fields = [f for f in FIELDS if getattr(args, f)] or list(FIELDS)
    results = [count_source(name) for name in (args.files or ["-"])]

    if args.format == "json":
        payload = [{"name": r.name, **{f: getattr(r, f) for f in fields}} for r in results]
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            values = " ".join(f"{getattr(r, f):>8}" for f in fields)
            print(f"{values} {r.name}")
    return 0


def count_source(name: str) -> Counts:
    log.info("counting %s", name)
    if name == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(name, encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            raise CLIError(f"no such file: {name}") from None
        except IsADirectoryError:
            raise CLIError(f"is a directory: {name}") from None
        except UnicodeDecodeError:
            raise CLIError(f"not a UTF-8 text file: {name}") from None
    return Counts(name=name, lines=text.count("\n"), words=len(text.split()), chars=len(text))
