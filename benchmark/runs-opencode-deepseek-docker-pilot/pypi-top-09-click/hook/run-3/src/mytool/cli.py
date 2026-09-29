"""Top-level command-line interface for mytool.

The parser is assembled from independent command modules so that new
subcommands can be added by dropping a module into ``mytool.commands`` and
registering it in :func:`build_parser`.
"""

from __future__ import annotations

import argparse
import logging
from typing import Optional, Sequence

from mytool import __version__
from mytool.commands import config, files, greet

LOGGER = logging.getLogger("mytool")


def build_parser() -> argparse.ArgumentParser:
    """Construct the full argument parser for the tool."""
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
        action="count",
        default=0,
        help="increase verbosity (-v for info, -vv for debug)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="only print errors",
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        default=None,
        help="path to the configuration file (default: ~/.config/mytool/config.json)",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="COMMAND",
        required=True,
    )
    greet.register(subparsers)
    files.register(subparsers)
    config.register(subparsers)
    return parser


def configure_logging(args: argparse.Namespace) -> None:
    """Translate ``--verbose``/``--quiet`` flags into a logging level."""
    if args.quiet:
        level = logging.ERROR
    elif args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args)

    handler = getattr(args, "handler", None)
    if handler is None:  # pragma: no cover - argparse enforces a command
        parser.print_help()
        return 2

    try:
        return handler(args)
    except BrokenPipeError:  # e.g. piping into `head`
        return 0
    except KeyboardInterrupt:
        LOGGER.error("interrupted")
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
