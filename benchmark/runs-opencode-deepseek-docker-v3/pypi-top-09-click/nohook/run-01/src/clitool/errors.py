"""Custom exceptions raised by clitool commands."""

from __future__ import annotations


class CliError(Exception):
    """A user-facing error.

    Raising this from a command handler prints a clean message to stderr and
    exits with status ``1`` instead of showing a traceback.
    """
