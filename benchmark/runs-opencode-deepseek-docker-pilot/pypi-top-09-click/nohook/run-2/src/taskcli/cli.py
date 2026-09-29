from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .commands import add, done, list as list_cmd, remove
from .context import Context
from .storage import Storage, StorageError

COMMANDS = (add, list_cmd, done, remove)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task",
        description="Manage a simple list of tasks.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print extra diagnostics to stderr",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="task store to use (default: $TASKCLI_DATA or XDG data dir)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    for module in COMMANDS:
        module.add_parser(subparsers)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 2

    context = Context(storage=Storage(args.data_file), verbose=args.verbose)
    try:
        return handler(args, context) or 0
    except StorageError as exc:
        print(f"{parser.prog}: error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f"{parser.prog}: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
