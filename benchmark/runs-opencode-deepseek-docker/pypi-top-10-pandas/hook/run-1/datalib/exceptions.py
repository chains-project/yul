"""Exception hierarchy for :mod:`datalib`."""

from __future__ import annotations


class DataLibError(Exception):
    """Base class for every error raised by :mod:`datalib`."""


class MissingColumnError(DataLibError, KeyError):
    """Raised when an operation references a column that does not exist."""

    def __init__(self, name):
        self.name = name
        super().__init__(f"unknown column: {name!r}")

    def __str__(self) -> str:  # KeyError.__str__ adds quotes, keep it clean
        return f"unknown column: {self.name!r}"


class CSVParseError(DataLibError):
    """Raised when a CSV source cannot be parsed into a table."""


class SchemaError(DataLibError):
    """Raised when a declared schema or value cast is invalid."""
