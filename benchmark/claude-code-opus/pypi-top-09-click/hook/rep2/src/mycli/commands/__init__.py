"""Subcommand registry.

Each command module exposes:
  register(subparsers)  adds its subparser and sets `func=run` via set_defaults
  run(args) -> int      executes the command and returns an exit code

To add a command, create a module here and append it to COMMANDS.
"""

from mycli.commands import count, greet

COMMANDS = [greet, count]
