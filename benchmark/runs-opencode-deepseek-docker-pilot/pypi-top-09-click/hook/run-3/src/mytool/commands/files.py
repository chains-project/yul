"""The ``files`` subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List


def register(subparsers: "argparse._SubParsersAction") -> None:
    parser = subparsers.add_parser(
        "files",
        help="list files in a directory",
        description="List the entries of a directory with optional filtering.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=Path("."),
        type=Path,
        help="directory to inspect (default: current directory)",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="include hidden files and directories",
    )
    parser.add_argument(
        "-e",
        "--extension",
        action="append",
        default=[],
        metavar="EXT",
        help="only show files with this extension (repeatable, e.g. -e .py -e .md)",
    )
    parser.add_argument(
        "--limit",
        type=non_negative_int,
        default=None,
        metavar="N",
        help="stop after showing N entries",
    )
    parser.set_defaults(handler=run)


def non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"expected a non-negative integer, got {value!r}")
    return number


def _matches(entry: Path, extensions: List[str]) -> bool:
    if not extensions:
        return True
    return entry.is_file() and entry.suffix in extensions


def run(args: argparse.Namespace) -> int:
    directory: Path = args.path
    if not directory.is_dir():
        print(f"error: not a directory: {directory}", file=sys.stderr)
        return 1

    entries = sorted(directory.iterdir(), key=lambda path: path.name)
    shown = 0
    for entry in entries:
        if not args.all and entry.name.startswith("."):
            continue
        if not _matches(entry, args.extension):
            continue
        suffix = "/" if entry.is_dir() else ""
        print(f"{entry.name}{suffix}")
        shown += 1
        if args.limit is not None and shown >= args.limit:
            break

    if shown == 0:
        print("(no matching entries)", file=sys.stderr)
    return 0
