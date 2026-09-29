"""The core :class:`Table` data structure used across :mod:`csvlib`."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Callable, Optional

from ._utils import uniquify


class Table:
    """A simple, column-oriented table of heterogeneous values.

    Rows are stored internally as mappings from column name to value, so both
    positional and name-based access are convenient.  The value ``None``
    represents a missing cell.

    Parameters
    ----------
    columns:
        Iterable of column names.  Names must be unique.
    rows:
        Optional iterable of rows.  Each row may be a mapping keyed by column
        name or a sequence whose length matches ``columns``.
    """

    def __init__(
        self,
        columns: Iterable[str],
        rows: Optional[Iterable[Any]] = None,
    ) -> None:
        names = [str(c) for c in columns]
        if len(set(names)) != len(names):
            raise ValueError("Column names must be unique")
        self._columns: list[str] = names
        self._rows: list[dict[str, Any]] = []
        if rows is not None:
            for row in rows:
                self._rows.append(self._normalize_row(row))

    # -- construction ---------------------------------------------------
    @classmethod
    def from_records(cls, records: Iterable[Mapping[str, Any]]) -> "Table":
        """Build a table from an iterable of mappings.

        Column order follows first appearance across the records.
        """
        records = list(records)
        columns: list[str] = []
        for record in records:
            for key in record:
                if key not in columns:
                    columns.append(key)
        return cls(columns, records)

    @classmethod
    def from_dataframe(cls, frame: Any) -> "Table":
        """Build a table from a :class:`pandas.DataFrame` (optional dependency)."""
        columns = [str(c) for c in frame.columns]
        rows = frame.itertuples(index=False, name=None)
        return cls(columns, rows)

    def to_dataframe(self) -> Any:
        """Return a :class:`pandas.DataFrame` (requires pandas to be installed)."""
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise ImportError(
                "to_dataframe() requires pandas; install it with 'pip install pandas'"
            ) from exc
        return pd.DataFrame(self.to_rows(), columns=self._columns)

    def _normalize_row(self, row: Any) -> dict[str, Any]:
        if isinstance(row, Mapping):
            extra = set(row) - set(self._columns)
            if extra:
                raise ValueError(f"Unknown columns in row: {sorted(map(str, extra))}")
            return {column: row.get(column) for column in self._columns}
        values = list(row)
        if len(values) != len(self._columns):
            raise ValueError(
                f"Row has {len(values)} values but table has "
                f"{len(self._columns)} columns"
            )
        return dict(zip(self._columns, values))

    # -- basic properties ----------------------------------------------
    @property
    def columns(self) -> list[str]:
        """The column names, in order (a copy)."""
        return list(self._columns)

    @property
    def num_rows(self) -> int:
        return len(self._rows)

    @property
    def num_columns(self) -> int:
        return len(self._columns)

    @property
    def shape(self) -> tuple[int, int]:
        return (self.num_rows, self.num_columns)

    def __len__(self) -> int:
        return len(self._rows)

    def __bool__(self) -> bool:
        return bool(self._rows)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        for row in self._rows:
            yield dict(row)

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            return self.column(key)
        if isinstance(key, slice):
            return [dict(row) for row in self._rows[key]]
        if isinstance(key, int):
            return dict(self._rows[key])
        raise TypeError(f"Indices must be str, int or slice, not {type(key).__name__}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self._columns == other._columns and self._rows == other._rows

    def __repr__(self) -> str:
        return f"Table(shape={self.shape}, columns={self._columns!r})"

    # -- access ---------------------------------------------------------
    def column(self, name: str) -> list[Any]:
        """Return all values of *name* as a list."""
        if name not in self._columns:
            raise KeyError(f"Unknown column: {name!r}")
        return [row[name] for row in self._rows]

    def row(self, index: int) -> dict[str, Any]:
        """Return a single row as a mapping (a copy)."""
        return dict(self._rows[index])

    def to_rows(self) -> list[list[Any]]:
        """Return the data as a list of value lists (no header)."""
        return [[row[column] for column in self._columns] for row in self._rows]

    def to_dicts(self) -> list[dict[str, Any]]:
        """Return the data as a list of mappings (copies)."""
        return [dict(row) for row in self._rows]

    def head(self, n: int = 5) -> "Table":
        return Table(self._columns, self._rows[:n])

    def tail(self, n: int = 5) -> "Table":
        return Table(self._columns, self._rows[-n:] if n else [])

    # -- structure manipulation ----------------------------------------
    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> "Table":
        """Return rows for which ``predicate(row)`` is truthy."""
        return Table(self._columns, [r for r in self._rows if predicate(dict(r))])

    def select(self, *columns: str) -> "Table":
        """Return a new table with only *columns*, in the given order."""
        unknown = [c for c in columns if c not in self._columns]
        if unknown:
            raise KeyError(f"Unknown column(s): {', '.join(map(repr, unknown))}")
        return Table(list(columns), [[row[c] for c in columns] for row in self._rows])

    def drop(self, *columns: str) -> "Table":
        """Return a new table without *columns*."""
        keep = [c for c in self._columns if c not in columns]
        return Table(keep, [[row[c] for c in keep] for row in self._rows])

    def rename(self, mapping: Mapping[str, str]) -> "Table":
        """Return a new table with columns renamed according to *mapping*."""
        new_columns = uniquify([mapping.get(c, c) for c in self._columns])
        renamed = dict(zip(self._columns, new_columns))
        rows = [{renamed[col]: value for col, value in row.items()} for row in self._rows]
        return Table(new_columns, rows)

    def add_column(self, name: str, values: Iterable[Any]) -> "Table":
        """Return a new table with *name* appended."""
        values = list(values)
        if len(values) != self.num_rows:
            raise ValueError(
                f"Expected {self.num_rows} values for new column, got {len(values)}"
            )
        new_columns = uniquify(self._columns + [name])
        if new_columns[-1] != str(name):
            raise ValueError(f"Column already exists: {name!r}")
        return Table(
            new_columns,
            [row + [value] for row, value in zip(self.to_rows(), values)],
        )

    def with_rows(self, rows: Iterable[Any]) -> "Table":
        """Return a new table with a different set of rows (same columns)."""
        return Table(self._columns, rows)
