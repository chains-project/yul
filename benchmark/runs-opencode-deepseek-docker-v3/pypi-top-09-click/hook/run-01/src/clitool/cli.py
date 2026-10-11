"""Command-line entry point for clitool.

Builds the argument parser, wires up subcommands, configures logging, and
dispatches to the selected command's handler.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from clitool import __version__
from clitool.commands import calc, config, greet, info

PROG = "clitool"

EPILOG = """\
examples:
  clitool greet Ada --count 2 --uppercase
  clitool calc add 1 2 3
  clitool config set color blue
  clitool info --json
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="A command-line tool with multiple subcommands.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        help="Increase output verbosity (-v for INFO, -vv for DEBUG).",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only show errors.",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="COMMAND",
        required=True,
    )
    greet.register(subparsers)
    calc.register(subparsers)
    config.register(subparsers)
    info.register(subparsers)
    return parser


def _configure_logging(verbosity: int, quiet: bool) -> None:
    if quiet:
        level = logging.ERROR
    elif verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose, args.quiet)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help(sys.stderr)
        return 2
    result: int = handler(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
