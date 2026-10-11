"""Top-level argument parser and entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from clitool import __version__
from clitool.commands import COMMANDS
from clitool.config import DEFAULT_CONFIG_PATH
from clitool.errors import CliError

log = logging.getLogger("clitool")


def build_parser() -> argparse.ArgumentParser:
    """Build the full argument parser including every subcommand."""
    parser = argparse.ArgumentParser(
        prog="clitool",
        description="A multi-command command-line tool.",
        epilog="Run 'clitool COMMAND --help' for command specific help.",
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
        help="increase log verbosity; repeat for more detail",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="only print errors",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        metavar="PATH",
        help="path to the configuration file (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        title="commands",
    )
    for register in COMMANDS:
        register(subparsers)

    parser.set_defaults(handler=None)
    return parser


def _configure_logging(args: argparse.Namespace) -> None:
    if args.quiet:
        level = logging.ERROR
    elif args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run clitool and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args)

    if args.handler is None:
        parser.print_help(sys.stderr)
        return 2

    try:
        result = args.handler(args)
    except CliError as exc:
        log.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        log.error("interrupted")
        return 130
    except BrokenPipeError:
        return 141

    return int(result) if result else 0


if __name__ == "__main__":
    sys.exit(main())
