"""An in-memory, column-aware container for tabular data."""

from __future__ import annotations

import csv

from .errors import ColumnNotFoundError
from .values import DTYPES


class Table:
    """A simple table of named columns and homogeneous-ish rows.

    ``columns`` is a list of unique column names, ``rows`` is a list of
    equally sized lists, and ``dtypes`` maps each column name to one of
    ``"int"``, ``"float"``, ``"bool"`` or ``"str"``.
    """

    def __init__(self, columns, rows, dtypes=None):
        self.columns = [str(name) for name in columns]
        if len(set(self.columns)) != len(self.columns):
            raise ValueError("column names must be unique")
        self.rows = [list(row) for row in rows]
        width = len(self.columns)
        for position, row in enumerate(self.rows, start=1):
            if len(row) != width:
                raise ValueError(
                    f"row {position} has {len(row)} value(s); expected {width}"
                )
        if dtypes is None:
            dtypes = {}
        unknown = set(dtypes) - set(self.columns)
        if unknown:
            raise ValueError(f"dtypes reference unknown columns: {sorted(unknown)}")
        self.dtypes = {name: dtypes.get(name, "str") for name in self.columns}
        for name, dtype in self.dtypes.items():
            if dtype not in DTYPES:
                raise ValueError(f"unsupported dtype {dtype!r} for column {name!r}")

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.to_dicts())

    def __repr__(self):
        return f"Table(columns={self.columns!r}, rows={len(self.rows)})"

    def __eq__(self, other):
        if not isinstance(other, Table):
            return NotImplemented
        return (
            self.columns == other.columns
            and self.dtypes == other.dtypes
            and self.rows == other.rows
        )

    @property
    def shape(self):
        """Return ``(row_count, column_count)``."""
        return (len(self.rows), len(self.columns))

    def index(self, column):
        """Return the positional index of *column*."""
        try:
            return self.columns.index(column)
        except ValueError as exc:
            raise ColumnNotFoundError(column) from exc

    def __contains__(self, column):
        return column in self.columns

    def __getitem__(self, column):
        position = self.index(column)
        return [row[position] for row in self.rows]

    def get(self, column, default=None):
        """Return a column's values or *default* when it does not exist."""
        if column not in self.columns:
            return default
        return self[column]

    def to_dicts(self):
        """Return the rows as a list of dictionaries."""
        return [dict(zip(self.columns, row)) for row in self.rows]

    @classmethod
    def from_dicts(cls, records, columns=None):
        """Build a table from an iterable of mappings."""
        records = list(records)
        if columns is None:
            columns = []
            for record in records:
                for key in record:
                    if key not in columns:
                        columns.append(key)
        rows = [[record.get(column) for column in columns] for record in records]
        return cls(columns, rows)

    def head(self, n=5):
        """Return a new table with at most the first *n* rows."""
        return self._with_rows(self.rows[:n])

    def select(self, columns):
        """Return a new table containing only *columns* (in order)."""
        if isinstance(columns, str):
            columns = [columns]
        positions = [self.index(column) for column in columns]
        rows = [[row[position] for position in positions] for row in self.rows]
        dtypes = {column: self.dtypes[column] for column in columns}
        return Table(columns, rows, dtypes)

    def where(self, predicate):
        """Return rows for which ``predicate(record_dict)`` is truthy."""
        rows = [
            row
            for row in self.rows
            if predicate(dict(zip(self.columns, row)))
        ]
        return self._with_rows(rows)

    def with_column(self, name, values, dtype=None):
        """Return a copy of the table with an extra column."""
        values = list(values)
        if len(values) != len(self.rows):
            raise ValueError("column length must match the table's row count")
        rows = [row + [value] for row, value in zip(self.rows, values)]
        dtypes = dict(self.dtypes)
        dtypes[name] = dtype or "str"
        return Table(self.columns + [name], rows, dtypes)

    def _with_rows(self, rows):
        return Table(self.columns, rows, self.dtypes)

    def to_csv(self, target, delimiter=",", encoding="utf-8", include_header=True):
        """Write the table to a path or file-like object."""
        if hasattr(target, "write"):
            return self._write_csv(
                target, delimiter, include_header
            )
        with open(target, "w", newline="", encoding=encoding) as handle:
            return self._write_csv(handle, delimiter, include_header)

    def _write_csv(self, handle, delimiter, include_header):
        writer = csv.writer(handle, delimiter=delimiter)
        if include_header:
            writer.writerow(self.columns)
        for row in self.rows:
            writer.writerow(["" if value is None else value for value in row])
