"""Command registration.

Each command module exposes a ``register(subparsers)`` function that attaches
an ``ArgumentParser`` to the top-level subparsers and wires up a handler with
``parser.set_defaults(handler=...)``.  New commands only need to be added to
``COMMANDS`` below.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable

from clitool.commands import config_cmd, hello, tasks

Registrar = Callable[[argparse._SubParsersAction], None]

COMMANDS: tuple[Registrar, ...] = (
    hello.register,
    tasks.register,
    config_cmd.register,
)

__all__ = ["COMMANDS", "Registrar"]
