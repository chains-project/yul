"""Top-level argument parser and entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from mycli import __version__
from mycli.commands import COMMANDS

log = logging.getLogger("mycli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A command-line tool with multiple subcommands.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="increase log verbosity (repeatable: -vv)",
    )
    verbosity.add_argument(
        "-q", "--quiet", action="store_true", help="only show errors",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for register in COMMANDS:
        register(subparsers)

    return parser


def _configure_logging(verbose: int, quiet: bool) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", stream=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose, args.quiet)
    log.debug("parsed args: %s", args)

    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # surface a clean message instead of a traceback
        if args.verbose >= 2:
            raise
        print(f"mycli: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
