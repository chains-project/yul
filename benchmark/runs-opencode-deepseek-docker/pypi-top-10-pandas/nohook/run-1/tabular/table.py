"""Core table type for the tabular package."""

from __future__ import annotations

import csv
import io
import os
from typing import Any, Iterable, Iterator, Mapping, Optional

from .analysis import AnalysisMixin
from .cleaning import CleaningMixin
from .errors import ColumnNotFoundError


class DataTable(CleaningMixin, AnalysisMixin):
    """A lightweight, dependency-free table of values.

    Rows are stored as mappings keyed by column name. Loading, cleaning and
    analysis are exposed as methods; cleaning methods return new tables and
    never mutate the receiver.
    """

    __slots__ = ("_columns", "_rows")

    def __init__(self, columns: Iterable[str], rows: Iterable[Any]) -> None:
        columns = list(columns)
        if not columns:
            raise ValueError("a table needs at least one column")
        if len(set(columns)) != len(columns):
            raise ValueError("column names must be unique")

        known = set(columns)
        normalized = []
        for index, row in enumerate(rows):
            if isinstance(row, Mapping):
                unknown = set(row) - known
                if unknown:
                    raise ValueError(f"row {index} has unknown columns: {sorted(unknown)}")
                normalized.append({column: row.get(column) for column in columns})
            else:
                values = list(row)
                if len(values) != len(columns):
                    raise ValueError(
                        f"row {index} has {len(values)} values, expected {len(columns)}"
                    )
                normalized.append(dict(zip(columns, values)))

        self._columns = tuple(columns)
        self._rows = normalized

    @classmethod
    def from_rows(cls, header: Iterable[str], rows: Iterable[Any]) -> "DataTable":
        """Build a table from a header and an iterable of row sequences."""
        return cls(list(header), [list(row) for row in rows])

    # ------------------------------------------------------------------
    # Introspection / access
    # ------------------------------------------------------------------
    @property
    def columns(self) -> tuple:
        """Column names, in order."""
        return self._columns

    @property
    def rows(self) -> list:
        """A copy of the table's rows as dictionaries."""
        return [dict(row) for row in self._rows]

    def column(self, name: str) -> list:
        """Return the values of a single column as a list."""
        self._require(name)
        return [row[name] for row in self._rows]

    def to_dicts(self) -> list:
        """Return the rows as a list of dictionaries."""
        return [dict(row) for row in self._rows]

    def to_columns(self) -> dict:
        """Return a mapping of column name to list of values."""
        return {column: self.column(column) for column in self._columns}

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[dict]:
        for row in self._rows:
            yield dict(row)

    def __getitem__(self, column: str) -> list:
        return self.column(column)

    def __contains__(self, column: object) -> bool:
        return column in self._columns

    def __repr__(self) -> str:
        return f"DataTable(rows={len(self._rows)}, columns={list(self._columns)})"

    # ------------------------------------------------------------------
    # CSV output
    # ------------------------------------------------------------------
    def to_csv(self, path: Any, delimiter: str = ",", encoding: str = "utf-8") -> None:
        """Write the table to ``path`` as CSV."""
        with open(os.fspath(path), "w", encoding=encoding, newline="") as handle:
            self._write(handle, delimiter)

    def to_csv_string(self, delimiter: str = ",") -> str:
        """Render the table as a CSV string."""
        buffer = io.StringIO()
        self._write(buffer, delimiter)
        return buffer.getvalue()

    def _write(self, handle: Any, delimiter: str) -> None:
        writer = csv.writer(handle, delimiter=delimiter)
        writer.writerow(self._columns)
        for row in self._rows:
            writer.writerow(
                ["" if row[column] is None else row[column] for column in self._columns]
            )

    # ------------------------------------------------------------------
    # Internal helpers used by the mixins
    # ------------------------------------------------------------------
    def _require(self, column: str) -> str:
        if column not in self._columns:
            raise ColumnNotFoundError(column)
        return column

    def _require_all(self, columns: Iterable[str]) -> None:
        for column in columns:
            self._require(column)

    def _clone(
        self,
        columns: Optional[Iterable[str]] = None,
        rows: Optional[Iterable[Any]] = None,
    ) -> "DataTable":
        columns = tuple(self._columns if columns is None else columns)
        rows = self._rows if rows is None else list(rows)
        if columns != self._columns:
            rows = [{column: row.get(column) for column in columns} for row in rows]
        return DataTable(columns, rows)
