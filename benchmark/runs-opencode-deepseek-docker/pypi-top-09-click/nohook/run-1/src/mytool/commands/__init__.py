"""Subcommand implementations.

Each module in this package exposes two callables:

``add_parser(subparsers)``
    Register the subcommand and its arguments, returning the created parser.

``run(args)``
    Execute the command and return an integer exit status (or ``None`` for 0).
"""

from mytool.commands import config, greet

COMMANDS = (greet, config)

__all__ = ["COMMANDS", "config", "greet"]
