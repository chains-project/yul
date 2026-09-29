"""Registration of all subcommands."""

from __future__ import annotations

import argparse
from importlib import import_module
from typing import Iterable

COMMANDS: Iterable[str] = ("add", "list", "done", "remove")


def register(subparsers: argparse._SubParsersAction) -> None:
    for name in COMMANDS:
        module = import_module(f"{__name__}.{name}")
        module.register(subparsers)
