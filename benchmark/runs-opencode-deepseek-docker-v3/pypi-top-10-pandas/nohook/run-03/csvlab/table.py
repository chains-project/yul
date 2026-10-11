"""Core in-memory table representation."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Sequence


class ColumnNotFoundError(KeyError):
    """Raised when a referenced column does not exist."""


class Table:
    """A column-oriented collection of rows stored as lists.

    Missing values are represented by ``None``. Rows are validated to have the
    same width as ``columns``.
    """

    def __init__(self, columns: Sequence[str], rows: Iterable[Sequence[Any]]):
        self.columns = [str(c) for c in columns]
        if len(set(self.columns)) != len(self.columns):
            raise ValueError(f"duplicate column names: {self.columns!r}")
        width = len(self.columns)
        self._rows: list[list[Any]] = []
        for position, row in enumerate(rows):
            values = list(row)
            if len(values) != width:
                raise ValueError(
                    f"row {position} has {len(values)} values, expected {width}"
                )
            self._rows.append(values)

    @property
    def n_rows(self) -> int:
        return len(self._rows)

    @property
    def n_cols(self) -> int:
        return len(self.columns)

    @property
    def shape(self) -> tuple[int, int]:
        return (self.n_rows, self.n_cols)

    @property
    def empty(self) -> bool:
        return not self._rows or not self.columns

    def __len__(self) -> int:
        return self.n_rows

    def __iter__(self) -> Iterator[dict[str, Any]]:
        for row in self._rows:
            yield dict(zip(self.columns, row))

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.column(key)
        if isinstance(key, int):
            return list(self._rows[key])
        raise TypeError("indices must be column names or row integers")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self.columns == other.columns and self._rows == other._rows

    def __repr__(self) -> str:
        return f"Table(columns={self.columns!r}, n_rows={self.n_rows})"

    def index(self, name: str) -> int:
        try:
            return self.columns.index(name)
        except ValueError as exc:
            raise ColumnNotFoundError(name) from exc

    def column(self, name: str) -> list[Any]:
        position = self.index(name)
        return [row[position] for row in self._rows]

    def column_or_none(self, name: str) -> list[Any] | None:
        if name not in self.columns:
            return None
        return self.column(name)

    def row(self, position: int) -> list[Any]:
        return list(self._rows[position])

    def head(self, n: int = 5) -> "Table":
        return Table(self.columns, self._rows[: max(n, 0)])

    def tail(self, n: int = 5) -> "Table":
        if n <= 0:
            return Table(self.columns, [])
        return Table(self.columns, self._rows[-n:])

    def to_rows(self) -> list[list[Any]]:
        return [list(row) for row in self._rows]

    def to_dicts(self) -> list[dict[str, Any]]:
        return list(self)

    def select(self, *names: str) -> "Table":
        positions = [self.index(name) for name in names]
        rows = [[row[p] for p in positions] for row in self._rows]
        return Table(names, rows)

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> "Table":
        rows = [row for row in self._rows if predicate(dict(zip(self.columns, row)))]
        return Table(self.columns, rows)

    def sort_by(
        self,
        name: str,
        *,
        reverse: bool = False,
        key: Callable[[Any], Any] | None = None,
    ) -> "Table":
        position = self.index(name)

        def sort_key(row: list[Any]) -> Any:
            value = row[position]
            if value is None:
                return (1, None)
            if key is not None:
                value = key(value)
            return (0, value)

        rows = sorted(self._rows, key=sort_key, reverse=reverse)
        return Table(self.columns, rows)

    def rename(self, mapping: dict[str, str]) -> "Table":
        columns = [mapping.get(name, name) for name in self.columns]
        return Table(columns, self.to_rows())

    def add_column(self, name: str, values: Iterable[Any] | Callable[[dict[str, Any]], Any]) -> "Table":
        if name in self.columns:
            raise ValueError(f"column already exists: {name!r}")
        if callable(values):
            new_values = [values(record) for record in self]
        else:
            new_values = list(values)
        if len(new_values) != self.n_rows:
            raise ValueError(
                f"expected {self.n_rows} values for new column, got {len(new_values)}"
            )
        rows = [row + [value] for row, value in zip(self._rows, new_values)]
        return Table(self.columns + [name], rows)

    def drop_columns(self, *names: str) -> "Table":
        drop = {self.index(name) for name in names}
        positions = [i for i in range(self.n_cols) if i not in drop]
        columns = [self.columns[i] for i in positions]
        rows = [[row[i] for i in positions] for row in self._rows]
        return Table(columns, rows)

    def map_column(self, name: str, func: Callable[[Any], Any]) -> "Table":
        position = self.index(name)
        rows = [list(row) for row in self._rows]
        for row in rows:
            row[position] = func(row[position])
        return Table(self.columns, rows)
