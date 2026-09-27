"""Command-line entry point: argument parsing and dispatch."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from mytool import __version__
from mytool.commands import COMMANDS


class Context:
    """Runtime state shared by the parsed subcommand and its handler."""

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.verbose = getattr(args, "verbose", False)
        self.quiet = getattr(args, "quiet", False)

    def info(self, message: str) -> None:
        if self.verbose and not self.quiet:
            print(message, file=sys.stderr)


def add_global_options(parser: argparse.ArgumentParser) -> None:
    """Add options accepted both before and after the subcommand."""
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="enable verbose output on stderr",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=argparse.SUPPRESS,
        help="suppress non-essential output",
    )


def build_parser() -> argparse.ArgumentParser:
    """Construct the full argument parser including all subcommands."""
    global_parser = argparse.ArgumentParser(add_help=False)
    add_global_options(global_parser)

    parser = argparse.ArgumentParser(
        prog="mytool",
        description="A command-line tool with multiple subcommands.",
        epilog="Run 'mytool <command> --help' for command-specific options.",
        parents=[global_parser],
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="<command>",
        required=True,
    )
    for module in COMMANDS:
        module.add_parser(subparsers, parents=[global_parser])

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse ``argv`` (defaulting to ``sys.argv``) and run the requested command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    context = Context(args)
    handler = args.func
    try:
        result = handler(context)
    except KeyboardInterrupt:
        print("aborted", file=sys.stderr)
        return 130
    return int(result) if result else 0


if __name__ == "__main__":
    raise SystemExit(main())
