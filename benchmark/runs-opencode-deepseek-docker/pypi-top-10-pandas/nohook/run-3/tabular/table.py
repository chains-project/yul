"""The core :class:`Table` data structure."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from typing import Any


class Table:
    """An in-memory table made of named columns and positional rows.

    Values are stored exactly as provided; conversion between strings and
    numbers is handled by the :mod:`tabular.cleaning` helpers.
    """

    def __init__(self, headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
        self.headers: list[str] = list(headers)
        self.rows: list[list[Any]] = [list(row) for row in rows]
        if self.headers:
            width = len(self.headers)
            for row in self.rows:
                if len(row) != width:
                    raise ValueError(
                        f"row has {len(row)} value(s) but table has {width} column(s)"
                    )

    @classmethod
    def from_dicts(
        cls,
        records: Iterable[Mapping[str, Any]],
        headers: Sequence[str] | None = None,
    ) -> Table:
        """Build a table from an iterable of mappings."""
        records = list(records)
        if headers is None:
            headers = list(records[0].keys()) if records else []
        rows = [[record.get(header) for header in headers] for record in records]
        return cls(headers, rows)

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(row_count, column_count)``."""
        return len(self.rows), len(self.headers)

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[list[Any]]:
        return iter(self.rows)

    def __getitem__(self, index: int | slice) -> list[Any] | list[list[Any]]:
        return self.rows[index]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self.headers == other.headers and self.rows == other.rows

    def __repr__(self) -> str:
        return f"Table(rows={len(self.rows)}, columns={self.headers!r})"

    def _index(self, name: str) -> int:
        try:
            return self.headers.index(name)
        except ValueError:
            raise KeyError(
                f"column {name!r} not found; available columns: {self.headers}"
            ) from None

    def column(self, name: str) -> list[Any]:
        """Return the values of a single column."""
        index = self._index(name)
        return [row[index] for row in self.rows]

    def to_dicts(self) -> list[dict[str, Any]]:
        """Return the rows as a list of column-name-to-value mappings."""
        return [dict(zip(self.headers, row)) for row in self.rows]

    def add_column(self, name: str, values: Iterable[Any]) -> Table:
        """Return a copy with a new column appended."""
        values = list(values)
        if len(values) != len(self.rows):
            raise ValueError(
                f"column {name!r} has {len(values)} value(s) but table has "
                f"{len(self.rows)} row(s)"
            )
        rows = [row + [value] for row, value in zip(self.rows, values)]
        return Table(self.headers + [name], rows)

    def drop_columns(self, *names: str) -> Table:
        """Return a copy without the named columns."""
        drop = {self._index(name) for name in names}
        headers = [h for i, h in enumerate(self.headers) if i not in drop]
        rows = [[v for i, v in enumerate(row) if i not in drop] for row in self.rows]
        return Table(headers, rows)

    def rename_columns(self, mapping: Mapping[str, str]) -> Table:
        """Return a copy with columns renamed according to ``mapping``."""
        headers = [mapping.get(header, header) for header in self.headers]
        return Table(headers, self.rows)

    def select(self, *names: str) -> Table:
        """Return a copy containing only the named columns, in order."""
        indexes = [self._index(name) for name in names]
        headers = [self.headers[i] for i in indexes]
        rows = [[row[i] for i in indexes] for row in self.rows]
        return Table(headers, rows)

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> Table:
        """Return a copy with only the rows for which ``predicate`` is true."""
        rows = [
            row
            for row in self.rows
            if predicate(dict(zip(self.headers, row)))
        ]
        return Table(self.headers, rows)

    def sort_by(
        self,
        name: str,
        *,
        reverse: bool = False,
        key: Callable[[Any], Any] | None = None,
    ) -> Table:
        """Return a copy sorted by a single column."""
        index = self._index(name)
        if key is not None:
            rows = sorted(
                self.rows, key=lambda row: key(row[index]), reverse=reverse
            )
        else:
            rows = sorted(self.rows, key=lambda row: row[index], reverse=reverse)
        return Table(self.headers, rows)

    def head(self, n: int = 5) -> Table:
        """Return the first ``n`` rows."""
        return Table(self.headers, self.rows[:n])

    def tail(self, n: int = 5) -> Table:
        """Return the last ``n`` rows."""
        return Table(self.headers, self.rows[-n:])

    def copy(self) -> Table:
        """Return a shallow copy of the table."""
        return Table(self.headers, self.rows)
