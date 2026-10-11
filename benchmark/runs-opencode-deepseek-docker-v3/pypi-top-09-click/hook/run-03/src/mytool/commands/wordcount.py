"""The ``wordcount`` subcommand."""

from __future__ import annotations

import argparse
import sys


def register(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "wordcount",
        help="Count lines, words, and characters.",
        description="Count lines, words, and characters in files (or stdin) like wc.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=argparse.FileType("r"),
        default=[sys.stdin],
        help="files to read; defaults to stdin",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--lines", action="store_true", help="count lines only")
    group.add_argument("-w", "--words", action="store_true", help="count words only")
    group.add_argument("-c", "--chars", action="store_true", help="count characters only")
    parser.set_defaults(func=run)
    return parser


def run(args: argparse.Namespace) -> int:
    show_all = not (args.lines or args.words or args.chars)
    totals = [0, 0, 0]

    for handle in args.files:
        text = handle.read()
        from_stdin = handle is sys.stdin
        if not from_stdin:
            handle.close()

        lines = text.count("\n")
        words = len(text.split())
        chars = len(text)
        counts = [lines, words, chars]
        totals = [total + count for total, count in zip(totals, counts)]

        suffix = "" if from_stdin else f" {handle.name}"
        print(f"{_format(counts, show_all, args)}{suffix}")

    if len(args.files) > 1:
        print(_format(totals, show_all, args), "total")

    return 0


def _format(counts: list[int], show_all: bool, args: argparse.Namespace) -> str:
    lines, words, chars = counts
    if show_all:
        return f"{lines:>7}{words:>8}{chars:>8}"
    if args.lines:
        return f"{lines:>7}"
    if args.words:
        return f"{words:>8}"
    return f"{chars:>8}"
