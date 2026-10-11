"""Command modules for clitool.

Each command module exposes:

* ``NAME``  - the subcommand name.
* ``HELP``  - a one-line description shown in ``--help``.
* ``configure(parser)`` - attaches arguments/options to its subparser.
* ``run(args)`` - executes the command and returns an exit code.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from clitool.commands import calc, config, greet


class Command:
    """A single subcommand registered with the top-level parser."""

    def __init__(self, name: str, help: str, configure: Callable, run: Callable) -> None:
        self.name = name
        self.help = help
        self.configure = configure
        self.run = run


def discover() -> Sequence[Command]:
    """Return every available command.

    Add new commands by importing the module above and appending it here.
    """
    modules = (greet, calc, config)
    return [
        Command(m.NAME, m.HELP, m.configure, m.run)  # type: ignore[attr-defined]
        for m in modules
    ]
