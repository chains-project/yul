"""Exceptions shared across commands."""


class CLIError(Exception):
    """An expected, user-facing error. Printed without a traceback."""
