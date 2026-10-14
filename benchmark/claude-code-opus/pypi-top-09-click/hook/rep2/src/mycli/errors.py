"""Exceptions that map to clean CLI error messages and exit codes."""


class CLIError(Exception):
    """An expected, user-facing error. Printed without a traceback."""

    exit_code = 1
