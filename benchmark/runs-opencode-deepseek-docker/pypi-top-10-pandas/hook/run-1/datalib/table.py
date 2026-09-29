"""The in-memory ``Table`` container used throughout :mod:`datalib`.

A :class:`Table` is an ordered collection of named columns backed by a list of
row mappings (``dict`` keyed by column name).  It intentionally has no external
dependencies so it can be used anywhere the standard library is available.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

from .exceptions import DataLibError, MissingColumnError


class Table:
    """An ordered, column-oriented table of rows.

    Parameters
    ----------
    columns:
        Ordered sequence of unique column names.
    rows:
        Iterable of rows.  Each row may be either a mapping keyed by column
        name (missing keys become ``None``) or a sequence of values whose
        length must match ``columns``.
    """

    __slots__ = ("columns", "rows")

    def __init__(self, columns: Sequence[str], rows: Iterable) -> None:
        cols = [str(c) for c in columns]
        if len(set(cols)) != len(cols):
            raise DataLibError("column names must be unique")
        self.columns: list[str] = cols

        materialized: list[dict[str, Any]] = []
        for row in rows:
            if isinstance(row, Mapping):
                materialized.append({c: row.get(c) for c in cols})
            else:
                values = list(row)
                if len(values) != len(cols):
                    raise DataLibError(
                        f"row has {len(values)} values but table has {len(cols)} columns"
                    )
                materialized.append(dict(zip(cols, values)))
        self.rows: list[dict[str, Any]] = materialized

    # ------------------------------------------------------------------
    # Basic container protocol
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self.columns == other.columns and self.rows == other.rows

    def __repr__(self) -> str:
        return f"Table(columns={self.columns!r}, rows={len(self.rows)})"

    def __getitem__(self, key):
        """Return a column (by name), a row (by index) or a slice of rows."""
        if isinstance(key, str):
            return self.column(key)
        if isinstance(key, slice):
            return self._replace_rows(self.rows[key])
        return self.rows[key]

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    @property
    def column_names(self) -> list[str]:
        """A copy of the ordered column names."""
        return list(self.columns)

    @property
    def shape(self) -> tuple[int, int]:
        """``(number of rows, number of columns)``."""
        return len(self.rows), len(self.columns)

    def has_column(self, name: str) -> bool:
        return name in self.columns

    def _require(self, name: str) -> None:
        if name not in self.columns:
            raise MissingColumnError(name)

    def column(self, name: str) -> list[Any]:
        """Return every value in ``name`` as a list, top to bottom."""
        self._require(name)
        return [row[name] for row in self.rows]

    def to_rows(self) -> list[list[Any]]:
        """Return the table as a list of value lists (headerless)."""
        return [[row[c] for c in self.columns] for row in self.rows]

    def to_dicts(self) -> list[dict[str, Any]]:
        """Return a shallow copy of the rows as plain dictionaries."""
        return [dict(row) for row in self.rows]

    # ------------------------------------------------------------------
    # Row/column selection
    # ------------------------------------------------------------------
    def head(self, n: int = 5) -> "Table":
        """The first ``n`` rows."""
        return self._replace_rows(self.rows[: max(n, 0)])

    def tail(self, n: int = 5) -> "Table":
        """The last ``n`` rows."""
        if n <= 0:
            return self._replace_rows([])
        return self._replace_rows(self.rows[-n:])

    def select(self, *columns: str) -> "Table":
        """Return a new table containing only ``columns`` (in that order)."""
        for name in columns:
            self._require(name)
        return Table(list(columns), [{c: row[c] for c in columns} for row in self.rows])

    def drop_column(self, *columns: str) -> "Table":
        """Return a new table with ``columns`` removed."""
        for name in columns:
            self._require(name)
        keep = [c for c in self.columns if c not in columns]
        return self.select(*keep)

    def rename(self, mapping: Mapping[str, str]) -> "Table":
        """Return a new table with columns renamed according to ``mapping``."""
        for old in mapping:
            self._require(old)
        new_columns = [mapping.get(c, c) for c in self.columns]
        if len(set(new_columns)) != len(new_columns):
            raise DataLibError("rename would create duplicate column names")
        renamed = []
        for row in self.rows:
            renamed.append({mapping.get(c, c): row[c] for c in self.columns})
        return Table(new_columns, renamed)

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> "Table":
        """Keep only rows for which ``predicate(row)`` is truthy."""
        return self._replace_rows([row for row in self.rows if predicate(row)])

    def sort_by(self, key: str, reverse: bool = False) -> "Table":
        """Return rows sorted by the values in column ``key``.

        ``None`` values sort after everything else, regardless of ``reverse``.
        """
        self._require(key)
        present = [row for row in self.rows if row[key] is not None]
        missing = [row for row in self.rows if row[key] is None]
        present.sort(key=lambda row: row[key], reverse=reverse)
        return self._replace_rows(present + missing)

    # ------------------------------------------------------------------
    # Column mutation helpers (all return new tables)
    # ------------------------------------------------------------------
    def add_column(
        self, name: str, values: Iterable[Any] | Callable[[dict[str, Any]], Any]
    ) -> "Table":
        """Return a new table with ``name`` appended.

        ``values`` may be a callable taking a row, or an iterable with one
        value per row.
        """
        if name in self.columns:
            raise DataLibError(f"column already exists: {name!r}")
        if callable(values):
            materialized = [values(row) for row in self.rows]
        else:
            materialized = list(values)
            if len(materialized) != len(self.rows):
                raise DataLibError(
                    f"expected {len(self.rows)} values, got {len(materialized)}"
                )
        rows = [
            {**row, name: materialized[i]} for i, row in enumerate(self.rows)
        ]
        return Table(self.columns + [name], rows)

    def map_column(self, name: str, func: Callable[[Any], Any]) -> "Table":
        """Return a new table with ``func`` applied to every value in ``name``."""
        self._require(name)

        def transform(row):
            return {**row, name: func(row[name])}

        return self._replace_rows([transform(row) for row in self.rows])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _replace_rows(self, rows: Iterable[Mapping[str, Any]]) -> "Table":
        return Table(self.columns, rows)
