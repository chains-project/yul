"""Subcommand modules.

Each module exposes ``register(subparsers)`` which adds its parser and wires
``func`` onto the namespace so :mod:`clitool.cli` can dispatch to it.
"""

from clitool.commands import calc, greet

# Order here controls the order shown in ``--help``.
COMMANDS = (greet, calc)

__all__ = ["COMMANDS", "calc", "greet"]
