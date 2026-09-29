"""Command-line entry point: parser construction and dispatch."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, commands
from .storage import Store, default_data_file

log = logging.getLogger("clitool")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clitool",
        description="Track tasks from the command line.",
        epilog="Run 'clitool COMMAND --help' for command-specific options.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase logging verbosity (repeat for more)",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=default_data_file(),
        metavar="PATH",
        help="task store location (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="COMMAND",
        required=True,
    )
    commands.register(subparsers)
    return parser


def configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    log.debug("using data file %s", args.data_file)
    store = Store(args.data_file)
    return args.func(args, store)


if __name__ == "__main__":
    sys.exit(main())
