"""Top-level argument parser and entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from mytool import __version__
from mytool.commands import config, greet, stats
from mytool.errors import CLIError

log = logging.getLogger("mytool")

# Each command module exposes ``register(subparsers)``, which adds its
# subparser and sets ``func`` to the handler. Add new commands here.
COMMANDS = (greet, stats, config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mytool",
        description="A command-line tool with multiple subcommands.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", action="count", default=0,
        help="increase log verbosity (repeatable: -vv)",
    )
    verbosity.add_argument(
        "-q", "--quiet", action="store_true", help="only log errors"
    )

    subparsers = parser.add_subparsers(
        title="commands", dest="command", metavar="<command>", required=True
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.quiet)
    log.debug("parsed arguments: %s", args)

    try:
        return args.func(args) or 0
    except CLIError as exc:
        print(f"mytool: error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
