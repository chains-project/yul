"""Core :class:`Table` structure and CSV loading/serialization.

The public entry point is :class:`Table`, an immutable-ish container of
column names plus row mappings. Loading from CSV performs lightweight type
inference so that numeric and boolean columns can be analyzed directly.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence, TextIO

from ._common import is_number
from . import analysis as _analysis
from . import cleaners as _cleaners

DEFAULT_MISSING_VALUES = (
    "",
    "na",
    "n/a",
    "null",
    "none",
    "nan",
    "-",
)

_TRUE_VALUES = {"true", "yes"}
_FALSE_VALUES = {"false", "no"}


def _infer_scalar(text: str) -> Any:
    """Infer int/float/bool from a stripped string, falling back to str."""
    lowered = text.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def _coerce_cell(value: Any, infer_types: bool, missing_values: set[str]) -> Any:
    if value is None:
        return None
    stripped = value.strip()
    if stripped.lower() in missing_values:
        return None
    if infer_types:
        return _infer_scalar(stripped)
    return value


def _format_cell(value: Any) -> Any:
    if value is None:
        return ""
    return value


class Table:
    """A column-oriented table backed by a list of row mappings."""

    def __init__(
        self,
        columns: Sequence[str],
        rows: Iterable[Mapping[str, Any]],
    ) -> None:
        self.columns: list[str] = list(columns)
        self._rows: list[dict[str, Any]] = [
            {col: row.get(col) for col in self.columns} for row in rows
        ]

    # ------------------------------------------------------------------
    # Construction / serialization
    # ------------------------------------------------------------------
    @classmethod
    def from_csv(
        cls,
        source: str | Path | TextIO,
        *,
        delimiter: str = ",",
        encoding: str = "utf-8",
        infer_types: bool = True,
        missing_values: Iterable[str] | None = None,
    ) -> "Table":
        """Load a CSV file (path or open file object) into a :class:`Table`."""
        missing = (
            set(DEFAULT_MISSING_VALUES)
            if missing_values is None
            else {m.lower() for m in missing_values}
        )

        close = False
        if isinstance(source, (str, Path)):
            handle: TextIO = open(source, newline="", encoding=encoding)
            close = True
        else:
            handle = source

        try:
            reader = csv.DictReader(handle, delimiter=delimiter)
            columns = list(reader.fieldnames or [])
            rows = [
                {col: _coerce_cell(raw.get(col), infer_types, missing) for col in columns}
                for raw in reader
            ]
        finally:
            if close:
                handle.close()

        return cls(columns, rows)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Sequence[Any]],
    ) -> "Table":
        """Build a table from a mapping of column name to values."""
        columns = list(data)
        lengths = {len(values) for values in data.values()}
        if len(lengths) > 1:
            raise ValueError("all columns must have the same length")
        size = lengths.pop() if lengths else 0
        rows = [
            {col: data[col][i] for col in columns}
            for i in range(size)
        ]
        return cls(columns, rows)

    @classmethod
    def from_records(
        cls,
        records: Iterable[Mapping[str, Any]],
        *,
        columns: Sequence[str] | None = None,
    ) -> "Table":
        """Build a table from an iterable of row mappings."""
        records = list(records)
        if columns is None:
            seen: list[str] = []
            for record in records:
                for key in record:
                    if key not in seen:
                        seen.append(key)
            columns = seen
        return cls(columns, records)

    def to_csv(
        self,
        destination: str | Path | TextIO,
        *,
        delimiter: str = ",",
        encoding: str = "utf-8",
        write_header: bool = True,
    ) -> None:
        """Write the table to a CSV file (path or open file object)."""
        close = False
        if isinstance(destination, (str, Path)):
            handle: TextIO = open(destination, "w", newline="", encoding=encoding)
            close = True
        else:
            handle = destination

        try:
            writer = csv.DictWriter(handle, fieldnames=self.columns, delimiter=delimiter)
            if write_header:
                writer.writeheader()
            for row in self._rows:
                writer.writerow({col: _format_cell(row.get(col)) for col in self.columns})
        finally:
            if close:
                handle.close()

    def to_records(self) -> list[dict[str, Any]]:
        """Return a copy of the rows as a list of dictionaries."""
        return [dict(row) for row in self._rows]

    def to_dict(self) -> dict[str, list[Any]]:
        """Return a copy of the data as a mapping of column name to values."""
        return {col: [row.get(col) for row in self._rows] for col in self.columns}

    # ------------------------------------------------------------------
    # Basic access
    # ------------------------------------------------------------------
    @property
    def rows(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._rows]

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        for row in self._rows:
            yield dict(row)

    def __getitem__(self, column: str) -> list[Any]:
        if column not in self.columns:
            raise KeyError(column)
        return [row.get(column) for row in self._rows]

    def __repr__(self) -> str:
        return f"Table(rows={len(self)}, columns={self.columns!r})"

    def head(self, n: int = 5) -> "Table":
        return Table(self.columns, self._rows[:n])

    def tail(self, n: int = 5) -> "Table":
        return Table(self.columns, self._rows[-n:] if n else [])

    def column(self, name: str) -> list[Any]:
        return self[name]

    def copy(self) -> "Table":
        return Table(self.columns, self._rows)

    def numeric_columns(self) -> list[str]:
        """Columns whose non-missing values are all numbers."""
        result = []
        for col in self.columns:
            values = [v for v in self[col] if v is not None]
            if values and all(is_number(v) for v in values):
                result.append(col)
        return result

    def categorical_columns(self) -> list[str]:
        return [col for col in self.columns if col not in self.numeric_columns()]

    # ------------------------------------------------------------------
    # Cleaning (delegates to :mod:`csvlab.cleaners`)
    # ------------------------------------------------------------------
    def drop_duplicates(self, subset: Sequence[str] | None = None) -> "Table":
        return _cleaners.drop_duplicates(self, subset)

    def drop_missing(
        self,
        *,
        how: str = "any",
        subset: Sequence[str] | None = None,
        threshold: float | None = None,
    ) -> "Table":
        return _cleaners.drop_missing(self, how=how, subset=subset, threshold=threshold)

    def fill_missing(
        self,
        value: Any = None,
        *,
        columns: Sequence[str] | None = None,
        strategy: str | None = None,
    ) -> "Table":
        return _cleaners.fill_missing(self, value, columns=columns, strategy=strategy)

    def strip_whitespace(self, columns: Sequence[str] | None = None) -> "Table":
        return _cleaners.strip_whitespace(self, columns)

    def rename_columns(self, mapping: Mapping[str, str]) -> "Table":
        return _cleaners.rename_columns(self, mapping)

    def normalize_headers(self) -> "Table":
        return _cleaners.normalize_headers(self)

    def cast_column(self, column: str, dtype: str) -> "Table":
        return _cleaners.cast_column(self, column, dtype)

    def replace_values(self, column: str, replacements: Mapping[Any, Any]) -> "Table":
        return _cleaners.replace_values(self, column, replacements)

    # ------------------------------------------------------------------
    # Analysis (delegates to :mod:`csvlab.analysis`)
    # ------------------------------------------------------------------
    def describe(self) -> dict[str, dict[str, Any]]:
        return _analysis.describe(self)

    def value_counts(
        self,
        column: str,
        *,
        top: int | None = None,
    ) -> list[tuple[Any, int]]:
        return _analysis.value_counts(self, column, top=top)

    def mean(self, column: str) -> float:
        return _analysis.mean(self, column)

    def median(self, column: str) -> float:
        return _analysis.median(self, column)

    def stdev(self, column: str) -> float:
        return _analysis.stdev(self, column)

    def correlation(self, column_a: str, column_b: str) -> float:
        return _analysis.correlation(self, column_a, column_b)

    def group_by(self, keys: Sequence[str]) -> dict[tuple, "Table"]:
        return _analysis.group_by(self, keys)

    def aggregate(
        self,
        by: Sequence[str],
        aggregations: Mapping[str, str | Callable[[list[Any]], Any]],
    ) -> "Table":
        return _analysis.aggregate(self, by, aggregations)
