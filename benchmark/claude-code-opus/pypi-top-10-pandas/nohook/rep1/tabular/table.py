"""The core Table container: an ordered, column-oriented collection of rows."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence


class Table:
    """An immutable-by-convention table stored as ordered columns.

    Missing values are represented as ``None``. Operations return new Tables
    rather than mutating in place, so calls can be chained.
    """

    def __init__(self, columns: Mapping[str, Sequence[Any]]):
        lengths = {len(v) for v in columns.values()}
        if len(lengths) > 1:
            raise ValueError(f"columns have mismatched lengths: {sorted(lengths)}")
        self._columns: dict[str, list[Any]] = {k: list(v) for k, v in columns.items()}
        self._nrows = lengths.pop() if lengths else 0

    # --- construction -----------------------------------------------------

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, Any]], columns: Sequence[str] | None = None) -> "Table":
        rows = list(rows)
        if columns is None:
            columns = []
            for row in rows:
                for key in row:
                    if key not in columns:
                        columns.append(key)
        return cls({c: [row.get(c) for row in rows] for c in columns})

    # --- basic access -----------------------------------------------------

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    @property
    def shape(self) -> tuple[int, int]:
        return self._nrows, len(self._columns)

    def __len__(self) -> int:
        return self._nrows

    def __getitem__(self, column: str) -> list[Any]:
        return list(self._columns[column])

    def __contains__(self, column: object) -> bool:
        return column in self._columns

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return self.rows()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Table) and self._columns == other._columns

    def rows(self) -> Iterator[dict[str, Any]]:
        names = self.columns
        for values in zip(*self._columns.values()):
            yield dict(zip(names, values))

    def row(self, index: int) -> dict[str, Any]:
        return {c: v[index] for c, v in self._columns.items()}

    def to_dict(self) -> dict[str, list[Any]]:
        return {k: list(v) for k, v in self._columns.items()}

    # --- structural transforms -------------------------------------------

    def select(self, *columns: str) -> "Table":
        return Table({c: self._columns[c] for c in columns})

    def drop(self, *columns: str) -> "Table":
        return Table({c: v for c, v in self._columns.items() if c not in columns})

    def rename(self, mapping: Mapping[str, str]) -> "Table":
        return Table({mapping.get(c, c): v for c, v in self._columns.items()})

    def with_column(self, name: str, values: Sequence[Any] | Callable[[dict[str, Any]], Any]) -> "Table":
        if callable(values):
            values = [values(r) for r in self.rows()]
        cols = self.to_dict()
        cols[name] = list(values)
        return Table(cols)

    def take(self, indices: Iterable[int]) -> "Table":
        indices = list(indices)
        return Table({c: [v[i] for i in indices] for c, v in self._columns.items()})

    def head(self, n: int = 5) -> "Table":
        return self.take(range(min(n, self._nrows)))

    def sort_by(self, column: str, reverse: bool = False) -> "Table":
        """Sort by a column; missing values always sort last."""
        values = self._columns[column]
        present = [i for i, v in enumerate(values) if v is not None]
        missing = [i for i, v in enumerate(values) if v is None]
        present.sort(key=lambda i: values[i], reverse=reverse)
        return self.take(present + missing)

    # --- fluent wrappers around module functions -------------------------

    def clean_column_names(self) -> "Table":
        from .clean import clean_column_names
        return clean_column_names(self)

    def strip_whitespace(self) -> "Table":
        from .clean import strip_whitespace
        return strip_whitespace(self)

    def drop_duplicates(self, subset: Sequence[str] | None = None) -> "Table":
        from .clean import drop_duplicates
        return drop_duplicates(self, subset)

    def drop_missing(self, subset: Sequence[str] | None = None, how: str = "any") -> "Table":
        from .clean import drop_missing
        return drop_missing(self, subset, how)

    def fill_missing(self, value: Any = None, strategy: str | None = None,
                     columns: Sequence[str] | None = None) -> "Table":
        from .clean import fill_missing
        return fill_missing(self, value, strategy, columns)

    def cast_column(self, column: str, type_: Callable[[Any], Any], errors: str = "raise") -> "Table":
        from .clean import cast_column
        return cast_column(self, column, type_, errors)

    def filter_rows(self, predicate: Callable[[dict[str, Any]], bool]) -> "Table":
        from .clean import filter_rows
        return filter_rows(self, predicate)

    def describe(self, columns: Sequence[str] | None = None) -> dict[str, dict[str, Any]]:
        from .analysis import describe
        return describe(self, columns)

    def value_counts(self, column: str, dropna: bool = True) -> list[tuple[Any, int]]:
        from .analysis import value_counts
        return value_counts(self, column, dropna)

    def correlation(self, columns: Sequence[str] | None = None) -> dict[str, dict[str, float | None]]:
        from .analysis import correlation
        return correlation(self, columns)

    def group_by(self, keys: str | Sequence[str], aggregations: Mapping[str, Any]) -> "Table":
        from .analysis import group_by
        return group_by(self, keys, aggregations)

    # --- display ----------------------------------------------------------

    def __repr__(self) -> str:
        return f"<Table {self._nrows} rows x {len(self._columns)} columns: {self.columns}>"

    def to_string(self, max_rows: int = 10) -> str:
        names = self.columns
        shown = [self.row(i) for i in range(min(max_rows, self._nrows))]
        cells = [[("" if r[c] is None else str(r[c])) for c in names] for r in shown]
        widths = [max([len(n)] + [len(row[j]) for row in cells]) for j, n in enumerate(names)]
        lines = ["  ".join(n.ljust(w) for n, w in zip(names, widths))]
        lines.append("  ".join("-" * w for w in widths))
        lines += ["  ".join(v.ljust(w) for v, w in zip(row, widths)) for row in cells]
        if self._nrows > max_rows:
            lines.append(f"... ({self._nrows - max_rows} more rows)")
        return "\n".join(lines)
