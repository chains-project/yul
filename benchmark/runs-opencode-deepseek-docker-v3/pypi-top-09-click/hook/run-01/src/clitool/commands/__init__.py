"""Subcommands for clitool.

Each command module exposes a ``register(subparsers)`` function that attaches
its parser and a handler via ``set_defaults(handler=...)``.
"""

from __future__ import annotations

__all__ = ["calc", "config", "greet", "info"]
