"""Top-level parser and entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Sequence

from mycli import __version__
from mycli.commands import config, count, greet
from mycli.errors import CLIError

log = logging.getLogger("mycli")

DEFAULT_CONFIG = Path.home() / ".config" / "mycli" / "config.json"

# Each command module exposes ``register(subparsers)``; add new commands here.
COMMANDS = (greet, count, config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A command-line tool with multiple subcommands.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", action="count", default=0, help="increase log verbosity (repeatable)"
    )
    verbosity.add_argument("-q", "--quiet", action="store_true", help="only show errors")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        metavar="PATH",
        help=f"config file to use (default: {DEFAULT_CONFIG})",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
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
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", stream=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.quiet)
    log.debug("parsed arguments: %s", args)

    try:
        return args.func(args) or 0
    except CLIError as exc:
        print(f"mycli: error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
