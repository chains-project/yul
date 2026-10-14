"""Core in-memory table type."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Sequence


class Table:
    """A simple column-oriented table.

    Rows are stored as lists aligned with ``columns``. Methods that transform
    the table return a new ``Table`` and leave the original untouched.
    """

    def __init__(self, columns: Sequence[str], rows: Iterable[Sequence[Any]] = ()):
        self.columns: list[str] = list(columns)
        if len(set(self.columns)) != len(self.columns):
            raise ValueError(f"duplicate column names: {self.columns}")
        self.rows: list[list[Any]] = []
        width = len(self.columns)
        for i, row in enumerate(rows):
            row = list(row)
            if len(row) != width:
                raise ValueError(f"row {i} has {len(row)} values, expected {width}")
            self.rows.append(row)

    @classmethod
    def from_dicts(cls, records: Iterable[dict[str, Any]]) -> Table:
        records = list(records)
        columns: list[str] = []
        for record in records:
            for key in record:
                if key not in columns:
                    columns.append(key)
        return cls(columns, ([r.get(c) for c in columns] for r in records))

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.to_dicts())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self.columns == other.columns and self.rows == other.rows

    def __repr__(self) -> str:
        return f"Table(columns={self.columns}, rows={len(self.rows)})"

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.columns)

    def _index(self, column: str) -> int:
        try:
            return self.columns.index(column)
        except ValueError:
            raise KeyError(column) from None

    def column(self, name: str) -> list[Any]:
        idx = self._index(name)
        return [row[idx] for row in self.rows]

    def __getitem__(self, name: str) -> list[Any]:
        return self.column(name)

    def to_dicts(self) -> list[dict[str, Any]]:
        return [dict(zip(self.columns, row)) for row in self.rows]

    def head(self, n: int = 5) -> Table:
        return Table(self.columns, self.rows[:n])

    def select(self, *columns: str) -> Table:
        idxs = [self._index(c) for c in columns]
        return Table(columns, ([row[i] for i in idxs] for row in self.rows))

    def drop(self, *columns: str) -> Table:
        for c in columns:
            self._index(c)
        return self.select(*[c for c in self.columns if c not in columns])

    def rename(self, mapping: dict[str, str]) -> Table:
        for c in mapping:
            self._index(c)
        return Table([mapping.get(c, c) for c in self.columns], self.rows)

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> Table:
        return Table(
            self.columns,
            (row for row in self.rows if predicate(dict(zip(self.columns, row)))),
        )

    def with_column(self, name: str, values_or_fn: Sequence[Any] | Callable[[dict[str, Any]], Any]) -> Table:
        """Add or replace a column from a sequence or a per-row function."""
        if callable(values_or_fn):
            values = [values_or_fn(r) for r in self.to_dicts()]
        else:
            values = list(values_or_fn)
            if len(values) != len(self.rows):
                raise ValueError(f"expected {len(self.rows)} values, got {len(values)}")
        if name in self.columns:
            idx = self._index(name)
            rows = [row[:idx] + [v] + row[idx + 1:] for row, v in zip(self.rows, values)]
            return Table(self.columns, rows)
        return Table(self.columns + [name], (row + [v] for row, v in zip(self.rows, values)))

    def sort_by(self, column: str, reverse: bool = False) -> Table:
        """Sort by a column; missing values (None) always sort last."""
        idx = self._index(column)
        present = [r for r in self.rows if r[idx] is not None]
        missing = [r for r in self.rows if r[idx] is None]
        present.sort(key=lambda r: r[idx], reverse=reverse)
        return Table(self.columns, present + missing)
