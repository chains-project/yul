"""Core column-oriented table container."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence


class Table:
    """An ordered collection of equally sized, named columns.

    Missing values are represented as ``None``. Tables are treated as
    immutable by the library: every cleaning/analysis function returns a new
    ``Table`` rather than modifying its input.
    """

    def __init__(self, columns: Mapping[str, Sequence[Any]]):
        lengths = {len(values) for values in columns.values()}
        if len(lengths) > 1:
            raise ValueError(f"columns have mismatched lengths: {sorted(lengths)}")
        self._columns: dict[str, list[Any]] = {
            name: list(values) for name, values in columns.items()
        }
        self._num_rows = lengths.pop() if lengths else 0

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, Any]],
                  columns: Sequence[str] | None = None) -> "Table":
        """Build a table from an iterable of row dicts."""
        rows = list(rows)
        if columns is None:
            columns = []
            for row in rows:
                for key in row:
                    if key not in columns:
                        columns.append(key)
        return cls({name: [row.get(name) for row in rows] for name in columns})

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    @property
    def shape(self) -> tuple[int, int]:
        return (self._num_rows, len(self._columns))

    def __len__(self) -> int:
        return self._num_rows

    def __contains__(self, name: object) -> bool:
        return name in self._columns

    def __getitem__(self, name: str) -> list[Any]:
        """Return a copy of the named column."""
        return list(self._columns[name])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Table) and self._columns == other._columns

    def __repr__(self) -> str:
        rows, cols = self.shape
        return f"Table(rows={rows}, columns={self.columns!r})"

    def rows(self) -> Iterator[dict[str, Any]]:
        """Iterate over rows as dicts."""
        names = self.columns
        for values in zip(*self._columns.values()):
            yield dict(zip(names, values))

    def row(self, index: int) -> dict[str, Any]:
        return {name: values[index] for name, values in self._columns.items()}

    def head(self, n: int = 5) -> "Table":
        return Table({name: values[:n] for name, values in self._columns.items()})

    def select(self, names: Sequence[str]) -> "Table":
        missing = [name for name in names if name not in self._columns]
        if missing:
            raise KeyError(f"unknown columns: {missing}")
        return Table({name: self._columns[name] for name in names})

    def drop(self, names: Sequence[str]) -> "Table":
        dropped = set(names)
        return Table({n: v for n, v in self._columns.items() if n not in dropped})

    def rename(self, mapping: Mapping[str, str]) -> "Table":
        return Table({mapping.get(n, n): v for n, v in self._columns.items()})

    def with_column(self, name: str, values: Sequence[Any]) -> "Table":
        """Return a copy with ``name`` added or replaced."""
        columns = dict(self._columns)
        columns[name] = list(values)
        return Table(columns)

    def take(self, indices: Iterable[int]) -> "Table":
        """Return a table containing only the rows at ``indices``."""
        indices = list(indices)
        return Table({n: [v[i] for i in indices] for n, v in self._columns.items()})

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> "Table":
        """Keep rows for which ``predicate(row_dict)`` is truthy."""
        return self.take(i for i, row in enumerate(self.rows()) if predicate(row))

    def sort(self, by: str | Sequence[str], descending: bool = False) -> "Table":
        """Sort rows by one or more columns; missing values always sort last."""
        keys = [by] if isinstance(by, str) else list(by)
        present, missing = [], []
        for i in range(self._num_rows):
            if any(self._columns[k][i] is None for k in keys):
                missing.append(i)
            else:
                present.append(i)
        present.sort(key=lambda i: tuple(self._columns[k][i] for k in keys),
                     reverse=descending)
        return self.take(present + missing)

    def to_dict(self) -> dict[str, list[Any]]:
        return {name: list(values) for name, values in self._columns.items()}
