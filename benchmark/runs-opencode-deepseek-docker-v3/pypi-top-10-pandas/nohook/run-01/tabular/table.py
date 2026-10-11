"""Core column-oriented table data structure."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence


class Table:
    """A table of column-oriented data.

    A :class:`Table` stores an ordered set of columns, each backed by a list of
    values of equal length. Missing values are represented by ``None``.

    Instances are treated as immutable by convention: every operation that
    transforms a table returns a new :class:`Table` rather than mutating the
    original.
    """

    def __init__(
        self,
        columns: Sequence[str],
        data: Optional[Mapping[str, Sequence[Any]]] = None,
    ) -> None:
        columns = list(columns)
        if len(set(columns)) != len(columns):
            raise ValueError("column names must be unique")

        data = {} if data is None else data
        normalized: Dict[str, List[Any]] = {}
        length: Optional[int] = None
        for name in columns:
            values = list(data.get(name, []))
            if length is None:
                length = len(values)
            elif len(values) != length:
                raise ValueError(
                    "all columns must have the same length "
                    f"(column {name!r} has {len(values)}, expected {length})"
                )
            normalized[name] = values

        self._columns = columns
        self._data = normalized
        self._length = 0 if length is None else length

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_rows(
        cls,
        columns: Sequence[str],
        rows: Iterable[Sequence[Any]],
    ) -> "Table":
        """Build a table from row-oriented data."""
        columns = list(columns)
        data: Dict[str, List[Any]] = {name: [] for name in columns}
        for index, row in enumerate(rows):
            values = list(row)
            if len(values) != len(columns):
                raise ValueError(
                    f"row {index} has {len(values)} values, expected {len(columns)}"
                )
            for name, value in zip(columns, values):
                data[name].append(value)
        return cls(columns, data)

    @classmethod
    def from_dicts(
        cls,
        records: Iterable[Mapping[str, Any]],
        columns: Optional[Sequence[str]] = None,
    ) -> "Table":
        """Build a table from an iterable of row dictionaries.

        When ``columns`` is omitted the column order is the order in which keys
        first appear across the records. Missing keys are filled with ``None``.
        """
        records = list(records)
        if columns is None:
            seen: Dict[str, None] = {}
            for record in records:
                for key in record:
                    seen.setdefault(key, None)
            columns = list(seen)

        columns = list(columns)
        data: Dict[str, List[Any]] = {name: [] for name in columns}
        for record in records:
            for name in columns:
                data[name].append(record.get(name))
        return cls(columns, data)

    # ------------------------------------------------------------------
    # Basic properties
    # ------------------------------------------------------------------
    @property
    def columns(self) -> List[str]:
        """The column names, in order."""
        return list(self._columns)

    @property
    def num_rows(self) -> int:
        return self._length

    @property
    def num_columns(self) -> int:
        return len(self._columns)

    @property
    def shape(self) -> tuple:
        """Return ``(num_rows, num_columns)``."""
        return (self._length, len(self._columns))

    def __len__(self) -> int:
        return self._length

    def __contains__(self, name: object) -> bool:
        return name in self._data

    def __getitem__(self, name: str) -> List[Any]:
        return self.column(name)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self.rows(named=True)

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------
    def column(self, name: str) -> List[Any]:
        """Return a copy of the values for ``name``."""
        if name not in self._data:
            raise KeyError(f"unknown column: {name!r}")
        return list(self._data[name])

    def row(self, index: int) -> Dict[str, Any]:
        """Return a single row as a dictionary."""
        if index < 0:
            index += self._length
        if not 0 <= index < self._length:
            raise IndexError("row index out of range")
        return {name: self._data[name][index] for name in self._columns}

    def rows(self, named: bool = False) -> Iterator[Any]:
        """Iterate over rows as lists, or dictionaries when ``named`` is true."""
        for index in range(self._length):
            if named:
                yield self.row(index)
            else:
                yield [self._data[name][index] for name in self._columns]

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Return the table as a list of row dictionaries."""
        return list(self.rows(named=True))

    def head(self, n: int = 5) -> "Table":
        """Return a new table with the first ``n`` rows."""
        n = max(0, n)
        return self._slice(0, min(n, self._length))

    def tail(self, n: int = 5) -> "Table":
        """Return a new table with the last ``n`` rows."""
        n = max(0, n)
        return self._slice(max(0, self._length - n), self._length)

    def _slice(self, start: int, stop: int) -> "Table":
        data = {name: values[start:stop] for name, values in self._data.items()}
        return Table(self._columns, data)

    # ------------------------------------------------------------------
    # Transformation
    # ------------------------------------------------------------------
    def select(self, columns: Sequence[str]) -> "Table":
        """Return a new table containing only ``columns``."""
        return Table(columns, {name: self.column(name) for name in columns})

    def drop(self, columns: Sequence[str]) -> "Table":
        """Return a new table without ``columns``."""
        drop = set(columns)
        missing = drop.difference(self._data)
        if missing:
            raise KeyError(f"unknown columns: {sorted(missing)!r}")
        keep = [name for name in self._columns if name not in drop]
        return Table(keep, {name: self.column(name) for name in keep})

    def rename(self, mapping: Mapping[str, str]) -> "Table":
        """Return a new table with columns renamed according to ``mapping``."""
        unknown = set(mapping).difference(self._data)
        if unknown:
            raise KeyError(f"unknown columns: {sorted(unknown)!r}")
        new_columns = [mapping.get(name, name) for name in self._columns]
        data = {
            mapping.get(name, name): self.column(name) for name in self._columns
        }
        return Table(new_columns, data)

    def with_column(self, name: str, values: Sequence[Any]) -> "Table":
        """Return a new table with ``name`` added or replaced."""
        values = list(values)
        if len(values) != self._length:
            raise ValueError(
                f"column {name!r} has {len(values)} values, expected {self._length}"
            )
        data = {col: self.column(col) for col in self._columns}
        data[name] = values
        columns = self._columns if name in self._data else self._columns + [name]
        return Table(columns, data)

    def filter(self, predicate) -> "Table":
        """Return a new table with rows for which ``predicate(row_dict)`` is true."""
        keep = [row for row in self.rows(named=True) if predicate(row)]
        return Table.from_dicts(keep, columns=self._columns)

    # ------------------------------------------------------------------
    # Comparison / display
    # ------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self._columns == other._columns and self._data == other._data

    def __repr__(self) -> str:
        return (
            f"Table(columns={self._columns!r}, rows={self._length}, "
            f"cols={len(self._columns)})"
        )
