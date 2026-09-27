"""Exception hierarchy for the tabular package."""

from __future__ import annotations

from typing import Any


class TabularError(Exception):
    """Base class for every error raised by :mod:`tabular`."""


class CSVLoadError(TabularError):
    """Raised when a CSV source cannot be read or parsed."""


class ColumnNotFoundError(TabularError, KeyError):
    """Raised when a requested column is not present in a table."""

    def __init__(self, column: Any) -> None:
        super().__init__(column)
        self.column = column

    def __str__(self) -> str:
        return f"unknown column: {self.column!r}"
