"""Top-level argument parser and command dispatch for ``mytool``."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from mytool import __version__
from mytool.commands import calc, greet, wordcount


def build_parser() -> argparse.ArgumentParser:
    """Construct the full argument parser with all subcommands registered."""
    parser = argparse.ArgumentParser(
        prog="mytool",
        description="A command-line tool with multiple subcommands.",
        epilog="Run 'mytool COMMAND --help' for command-specific options.",
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
        help="increase verbosity (repeatable, e.g. -vv)",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="COMMAND",
        required=True,
    )

    greet.register(subparsers)
    calc.register(subparsers)
    wordcount.register(subparsers)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv`` and run the selected command, returning its exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
