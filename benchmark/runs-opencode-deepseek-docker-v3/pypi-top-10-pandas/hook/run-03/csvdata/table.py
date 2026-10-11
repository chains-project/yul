"""Core in-memory table type used across the csvdata library."""

from __future__ import annotations

from typing import Any, Iterable, Iterator, Sequence

MISSING = (None, "")


def is_missing(value: Any) -> bool:
    """Return True when *value* should be treated as a missing cell."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, float):
        return value != value  # NaN
    return False


class Table:
    """An ordered collection of named columns and row records.

    Rows are stored as dictionaries keyed by column name. All values are
    kept as-is on construction; use :mod:`csvdata.clean` to coerce types.
    """

    def __init__(self, columns: Sequence[str], rows: Iterable[dict]):
        self._columns = list(columns)
        seen = set()
        for column in self._columns:
            if column in seen:
                raise ValueError(f"duplicate column name: {column!r}")
            seen.add(column)
        self._rows = [self._normalize_row(row) for row in rows]

    def _normalize_row(self, row: dict) -> dict:
        missing = [c for c in self._columns if c not in row]
        if missing:
            raise KeyError(f"row is missing columns: {missing}")
        return {column: row[column] for column in self._columns}

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    @property
    def rows(self) -> list[dict]:
        return [dict(row) for row in self._rows]

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self._rows), len(self._columns))

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[dict]:
        return iter(self._rows)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self._columns == other._columns and self._rows == other._rows

    def __repr__(self) -> str:
        return f"Table(shape={self.shape}, columns={self._columns})"

    def column(self, name: str) -> list[Any]:
        """Return the values of *name* as a list, one per row."""
        self._require_column(name)
        return [row[name] for row in self._rows]

    def head(self, n: int = 5) -> list[dict]:
        """Return the first *n* rows."""
        return [dict(row) for row in self._rows[:n]]

    def select(self, *columns: str) -> "Table":
        """Return a new table containing only *columns*, in the given order."""
        for column in columns:
            self._require_column(column)
        rows = [{c: row[c] for c in columns} for row in self._rows]
        return Table(list(columns), rows)

    def filter(self, predicate) -> "Table":
        """Return a new table with rows for which ``predicate(row)`` is true."""
        return Table(self._columns, [row for row in self._rows if predicate(row)])

    def to_dicts(self) -> list[dict]:
        return self.rows

    def _require_column(self, name: str) -> None:
        if name not in self._columns:
            raise KeyError(f"unknown column: {name!r}")
