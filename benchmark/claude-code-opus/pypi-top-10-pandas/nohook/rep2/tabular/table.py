"""Core in-memory table type."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

Row = dict[str, Any]


class Table:
    """An ordered collection of rows sharing a fixed set of named columns.

    Tables are treated as immutable: every transformation returns a new
    ``Table`` and leaves the original untouched. Missing values are ``None``.
    """

    def __init__(self, columns: Sequence[str], rows: Iterable[Mapping[str, Any]] = ()):
        if len(set(columns)) != len(columns):
            raise ValueError(f"duplicate column names: {list(columns)}")
        self._columns = list(columns)
        self._rows = [{c: row.get(c) for c in self._columns} for row in rows]

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    @property
    def rows(self) -> list[Row]:
        return [dict(r) for r in self._rows]

    @property
    def shape(self) -> tuple[int, int]:
        return len(self._rows), len(self._columns)

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[Row]:
        return (dict(r) for r in self._rows)

    def __getitem__(self, column: str) -> list[Any]:
        return self.column(column)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self._columns == other._columns and self._rows == other._rows

    def __repr__(self) -> str:
        n, m = self.shape
        return f"Table({n} rows x {m} columns: {self._columns})"

    def column(self, name: str) -> list[Any]:
        self._check_columns([name])
        return [r[name] for r in self._rows]

    def select(self, columns: Sequence[str]) -> Table:
        self._check_columns(columns)
        return Table(columns, self._rows)

    def filter(self, predicate: Callable[[Row], bool]) -> Table:
        return Table(self._columns, (r for r in self._rows if predicate(dict(r))))

    def sort(self, by: str | Sequence[str], descending: bool = False) -> Table:
        """Sort by one or more columns; missing values always sort last."""
        keys = [by] if isinstance(by, str) else list(by)
        self._check_columns(keys)
        rows = list(self._rows)
        # Stable sorts applied from the least to the most significant key.
        for key in reversed(keys):
            present = [r for r in rows if r[key] is not None]
            missing = [r for r in rows if r[key] is None]
            present.sort(key=lambda r: r[key], reverse=descending)
            rows = present + missing
        return Table(self._columns, rows)

    def head(self, n: int = 5) -> Table:
        return Table(self._columns, self._rows[:n])

    def with_column(self, name: str, values: Sequence[Any] | Callable[[Row], Any]) -> Table:
        """Add or replace a column, from a list of values or a per-row function."""
        if callable(values):
            values = [values(dict(r)) for r in self._rows]
        if len(values) != len(self._rows):
            raise ValueError(f"expected {len(self._rows)} values, got {len(values)}")
        columns = self._columns if name in self._columns else self._columns + [name]
        return Table(columns, ({**r, name: v} for r, v in zip(self._rows, values)))

    def rename(self, mapping: Mapping[str, str]) -> Table:
        self._check_columns(mapping.keys())
        columns = [mapping.get(c, c) for c in self._columns]
        return Table(columns, ({mapping.get(k, k): v for k, v in r.items()} for r in self._rows))

    def _check_columns(self, columns: Iterable[str]) -> None:
        unknown = [c for c in columns if c not in self._columns]
        if unknown:
            raise KeyError(f"unknown column(s): {unknown}")
