"""Command-line entry point and argument parsing for ``clitool``."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional, Sequence

from clitool import __version__
from clitool.commands import COMMANDS

log = logging.getLogger("clitool")


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser with global options and subcommands."""
    parser = argparse.ArgumentParser(
        prog="clitool",
        description="A command-line tool with multiple subcommands.",
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
        help="increase verbosity (repeatable: -v, -vv)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="only print errors",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="<command>",
        required=True,
        title="commands",
    )
    for module in COMMANDS:
        module.register(subparsers)
    return parser


def configure_logging(verbose: int, quiet: bool) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse *argv* and dispatch to the selected subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.quiet)
    log.debug("dispatching command %r", args.command)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
