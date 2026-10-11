"""Command-line entry point for clitool."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from clitool import __version__
from clitool.commands import discover

log = logging.getLogger("clitool")


def build_parser() -> argparse.ArgumentParser:
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
        help="increase output verbosity (-v, -vv)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    for command in discover():
        sub = subparsers.add_parser(
            command.name,
            help=command.help,
            description=command.help,
        )
        command.configure(sub)
        sub.set_defaults(_run=command.run)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING - 10 * min(args.verbose, 2),
        format="%(levelname)s: %(message)s",
    )

    run = getattr(args, "_run", None)
    if run is None:
        parser.print_help()
        return 2

    log.debug("dispatching command %r with %r", args.command, vars(args))
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
