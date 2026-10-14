"""``mycli count``: count lines, words, and characters (like ``wc``)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mycli.errors import CLIError

FIELDS = ("lines", "words", "chars")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "count",
        help="count lines, words, and characters",
        description="Count lines, words, and characters in files. Use '-' for stdin.",
    )
    p.add_argument(
        "files",
        nargs="*",
        default=["-"],
        metavar="FILE",
        help="files to read; '-' means stdin (default: stdin)",
    )
    p.add_argument("-l", "--lines", action="store_true", help="show line count")
    p.add_argument("-w", "--words", action="store_true", help="show word count")
    p.add_argument("-c", "--chars", action="store_true", help="show character count")
    p.set_defaults(func=run)


def count_text(text: str) -> dict[str, int]:
    return {"lines": text.count("\n"), "words": len(text.split()), "chars": len(text)}


def run(args: argparse.Namespace) -> int:
    selected = [f for f in FIELDS if getattr(args, f)] or list(FIELDS)
    totals = dict.fromkeys(FIELDS, 0)

    for name in args.files:
        counts = count_text(_read(name))
        for f in FIELDS:
            totals[f] += counts[f]
        _print_row(counts, selected, name)

    if len(args.files) > 1:
        _print_row(totals, selected, "total")
    return 0


def _read(name: str) -> str:
    if name == "-":
        return sys.stdin.read()
    try:
        return Path(name).read_text(encoding="utf-8")
    except OSError as exc:
        raise CLIError(f"cannot read {name}: {exc.strerror}") from exc


def _print_row(counts: dict[str, int], selected: list[str], label: str) -> None:
    cols = " ".join(f"{counts[f]:>8}" for f in selected)
    print(f"{cols} {label}")
