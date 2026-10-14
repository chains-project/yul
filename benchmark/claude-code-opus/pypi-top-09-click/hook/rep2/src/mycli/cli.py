"""Top-level argument parser and entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from mycli import __version__
from mycli.commands import COMMANDS
from mycli.errors import CLIError

log = logging.getLogger("mycli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A command-line tool with multiple subcommands.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase verbosity (-v, -vv)"
    )
    verbosity.add_argument("-q", "--quiet", action="store_true", help="only print errors")

    subparsers = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for command in COMMANDS:
        command.register(subparsers)
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
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", stream=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.quiet)
    log.debug("parsed arguments: %s", args)

    try:
        return args.func(args)
    except CLIError as exc:
        print(f"mycli: error: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
