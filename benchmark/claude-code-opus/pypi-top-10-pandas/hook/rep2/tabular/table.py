"""Column-oriented in-memory table."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from typing import Any

Row = dict[str, Any]


class Table:
    """An immutable, column-oriented table.

    Every column holds the same number of values; missing values are ``None``.
    Operations return new tables rather than mutating in place.
    """

    def __init__(self, columns: Mapping[str, Sequence[Any]]):
        lengths = {len(values) for values in columns.values()}
        if len(lengths) > 1:
            raise ValueError(f"columns have unequal lengths: {sorted(lengths)}")
        self._columns: dict[str, list[Any]] = {
            name: list(values) for name, values in columns.items()
        }
        self._length = lengths.pop() if lengths else 0

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, Any]], columns: Sequence[str] | None = None) -> Table:
        """Build a table from row mappings. Keys absent from a row become ``None``."""
        rows = list(rows)
        if columns is None:
            columns = list(dict.fromkeys(key for row in rows for key in row))
        return cls({name: [row.get(name) for row in rows] for name in columns})

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    @property
    def shape(self) -> tuple[int, int]:
        return self._length, len(self._columns)

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, name: str) -> list[Any]:
        return list(self._columns[name])

    def __contains__(self, name: object) -> bool:
        return name in self._columns

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Table) and self._columns == other._columns

    def __iter__(self) -> Iterator[Row]:
        return self.rows()

    def __repr__(self) -> str:
        return f"Table(rows={self._length}, columns={self.columns})"

    def rows(self) -> Iterator[Row]:
        names = self.columns
        for values in zip(*self._columns.values()):
            yield dict(zip(names, values))

    def head(self, n: int = 5) -> Table:
        return Table({name: values[:n] for name, values in self._columns.items()})

    def select(self, *names: str) -> Table:
        missing = [name for name in names if name not in self._columns]
        if missing:
            raise KeyError(f"unknown columns: {missing}")
        return Table({name: self._columns[name] for name in names})

    def rename(self, mapping: Mapping[str, str]) -> Table:
        return Table({mapping.get(name, name): values for name, values in self._columns.items()})

    def with_column(self, name: str, values: Sequence[Any] | Callable[[Row], Any]) -> Table:
        """Add or replace a column from a sequence or a function of each row."""
        if callable(values):
            values = [values(row) for row in self.rows()]
        return Table({**self._columns, name: values})

    def filter(self, predicate: Callable[[Row], bool]) -> Table:
        return Table.from_rows((row for row in self.rows() if predicate(row)), self.columns)

    def sort_by(self, name: str, *, descending: bool = False) -> Table:
        """Sort by one column. Missing values always sort last."""
        values = self._columns[name]
        present = [i for i, value in enumerate(values) if value is not None]
        absent = [i for i, value in enumerate(values) if value is None]
        present.sort(key=values.__getitem__, reverse=descending)
        order = present + absent
        return Table({col: [vals[i] for i in order] for col, vals in self._columns.items()})

    def to_rows(self) -> list[Row]:
        return list(self.rows())

    def to_string(self, max_rows: int = 20) -> str:
        """Render as an aligned plain-text grid."""
        shown = self.head(max_rows)
        cells = [self.columns] + [
            ["" if value is None else str(value) for value in row.values()] for row in shown.rows()
        ]
        widths = [max(len(row[i]) for row in cells) for i in range(len(self.columns))]
        lines = ["  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in cells]
        if self._length > max_rows:
            lines.append(f"... ({self._length - max_rows} more rows)")
        return "\n".join(lines)
