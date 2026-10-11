"""Subcommand registry.

Each command lives in its own module and exposes a ``register(subparsers,
common)`` function that adds its parser(s). Adding a command is a matter of
dropping a module in this package and listing it in :data:`MODULES`.
"""

from __future__ import annotations

import argparse
from importlib import import_module

MODULES = ("greet", "config")


def register_commands(
    subparsers: argparse._SubParsersAction,
    common: argparse.ArgumentParser,
) -> None:
    """Import each command module and let it register its subparser."""
    for name in MODULES:
        module = import_module(f"{__name__}.{name}")
        module.register(subparsers, common)
