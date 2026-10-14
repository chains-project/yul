"""Subcommands.

Each command module exposes ``register(subparsers)``, which adds its parser and
sets ``handler`` to a function taking the parsed args and returning an exit code.
To add a command, create a module here and append its ``register`` to COMMANDS.
"""

from mycli.commands import count, greet

COMMANDS = [greet.register, count.register]
