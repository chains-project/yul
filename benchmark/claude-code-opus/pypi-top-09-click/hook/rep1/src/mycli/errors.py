"""Exceptions shared across commands."""


class CommandError(Exception):
    """An expected failure; printed as a one-line error without a traceback."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code
