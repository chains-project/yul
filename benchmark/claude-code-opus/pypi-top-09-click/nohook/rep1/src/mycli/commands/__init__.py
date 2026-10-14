"""Subcommand registry.

Each subcommand module exposes ``register(subparsers)``, which adds its parser
and sets ``func`` to a handler taking the parsed ``argparse.Namespace`` and
returning an exit code. To add a command, create a module and list it here.
"""

from mycli.commands import greet, stats

COMMANDS = [greet.register, stats.register]
