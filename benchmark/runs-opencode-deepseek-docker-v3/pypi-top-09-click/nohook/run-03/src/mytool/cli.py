"""Command-line entry point, option parsing and subcommand dispatch."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .commands import register_commands


def build_common_parser() -> argparse.ArgumentParser:
    """Options shared by every subcommand.

    ``default=argparse.SUPPRESS`` keeps an option that is absent on a
    subcommand from overwriting a value already parsed at the top level.
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="enable verbose output",
    )
    return common


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser with all subcommands registered."""
    parser = argparse.ArgumentParser(
        prog="mytool",
        description="A command-line tool with multiple subcommands.",
        epilog="Run 'mytool COMMAND --help' for help on a specific command.",
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
        help="enable verbose output",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="commands",
    )
    register_commands(subparsers, build_common_parser())
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse ``argv`` and run the selected command.

    Returns the process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help(sys.stderr)
        return 2

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
