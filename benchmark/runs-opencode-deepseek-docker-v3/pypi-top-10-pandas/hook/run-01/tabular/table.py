"""Core in-memory table container used across the :mod:`tabular` package."""

from __future__ import annotations

from typing import Any, Callable, Iterator, Sequence


class Table:
    """A simple, dependency-free columnar table.

    Rows are stored as lists aligned with :attr:`columns`. Cells are expected
    to be ``None`` (missing) or a scalar value (``str``, ``int``, ``float``,
    ``bool``).
    """

    def __init__(
        self,
        columns: Sequence[str],
        rows: Sequence[Sequence[Any]] | None = None,
    ) -> None:
        self.columns: list[str] = list(columns)
        if len(set(self.columns)) != len(self.columns):
            raise ValueError("column names must be unique")
        self.rows: list[list[Any]] = []
        for row in rows or []:
            self._append(list(row))

    # -- construction helpers -------------------------------------------------

    def _append(self, row: list[Any]) -> None:
        if len(row) != len(self.columns):
            raise ValueError(
                f"row has {len(row)} values, expected {len(self.columns)}"
            )
        self.rows.append(row)

    def copy(self) -> "Table":
        """Return a deep-enough copy (new row lists, shared cell values)."""
        return Table(self.columns, [list(row) for row in self.rows])

    # -- container protocol ---------------------------------------------------

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.to_dicts())

    def __getitem__(self, key: int | str) -> Any:
        if isinstance(key, int):
            return self.to_dicts()[key]
        return self.column(key)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self.columns == other.columns and self.rows == other.rows

    def __repr__(self) -> str:
        return f"Table(columns={self.columns!r}, rows={len(self.rows)})"

    # -- column access --------------------------------------------------------

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(n_rows, n_columns)``."""
        return (len(self.rows), len(self.columns))

    def _index(self, column: str) -> int:
        try:
            return self.columns.index(column)
        except ValueError as exc:
            raise KeyError(column) from exc

    def column(self, name: str) -> list[Any]:
        """Return all values of ``name`` as a list."""
        index = self._index(name)
        return [row[index] for row in self.rows]

    def column_index(self, name: str) -> int:
        return self._index(name)

    def to_dicts(self) -> list[dict[str, Any]]:
        """Return rows as a list of ``{column: value}`` dicts."""
        return [dict(zip(self.columns, row)) for row in self.rows]

    def add_column(self, name: str, values: Sequence[Any]) -> None:
        """Append a new column. ``values`` must match the row count."""
        if name in self.columns:
            raise ValueError(f"column {name!r} already exists")
        if len(values) != len(self.rows):
            raise ValueError(
                f"expected {len(self.rows)} values, got {len(values)}"
            )
        self.columns.append(name)
        for row, value in zip(self.rows, values):
            row.append(value)

    def remove_column(self, name: str) -> None:
        """Drop a column in place."""
        index = self._index(name)
        del self.columns[index]
        for row in self.rows:
            del row[index]

    def rename_column(self, old: str, new: str) -> None:
        """Rename a column in place."""
        if new in self.columns and new != old:
            raise ValueError(f"column {new!r} already exists")
        self.columns[self._index(old)] = new

    # -- row operations -------------------------------------------------------

    def head(self, n: int = 5) -> "Table":
        """Return a new table with the first ``n`` rows."""
        return Table(self.columns, self.rows[:n])

    def tail(self, n: int = 5) -> "Table":
        """Return a new table with the last ``n`` rows."""
        return Table(self.columns, self.rows[-n:] if n else [])

    def select(self, columns: Sequence[str]) -> "Table":
        """Return a new table containing only ``columns``."""
        indices = [self._index(name) for name in columns]
        rows = [[row[i] for i in indices] for row in self.rows]
        return Table(columns, rows)

    def filter(
        self, predicate: Callable[[dict[str, Any]], bool]
    ) -> "Table":
        """Return rows for which ``predicate(row_dict)`` is true."""
        kept = [row for row in self.to_dicts() if predicate(row)]
        return Table(self.columns, [list(r.values()) for r in kept])

    def sort_by(self, column: str, reverse: bool = False) -> "Table":
        """Return a new table sorted by ``column`` (nulls last)."""
        index = self._index(column)

        def key(row: list[Any]) -> tuple[bool, Any]:
            value = row[index]
            return (value is None, value)

        try:
            rows = sorted(self.rows, key=key, reverse=reverse)
        except TypeError as exc:
            raise TypeError(
                f"cannot sort by {column!r}: mixed value types"
            ) from exc
        return Table(self.columns, rows)
