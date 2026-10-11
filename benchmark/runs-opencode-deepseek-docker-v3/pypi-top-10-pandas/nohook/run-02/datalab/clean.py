"""Cleaning operations for :mod:`datalab`.

Every function takes a :class:`~datalab.table.Table` and returns a new one;
the input is never modified.
"""

from __future__ import annotations

import statistics
from collections import Counter
from typing import Any, Callable, Iterable, List, Mapping, Optional, Sequence, Union

from .table import Table, is_missing, to_number

__all__ = [
    "strip_whitespace",
    "drop_empty_rows",
    "drop_duplicates",
    "drop_missing",
    "fill_missing",
    "rename_columns",
    "drop_columns",
    "replace_values",
    "convert_types",
    "coerce_numeric",
]


def _resolve(table: Table, columns: Optional[Sequence[str]]) -> List[str]:
    if columns is None:
        return table.headers
    resolved = []
    for name in columns:
        table.column(name)  # raises ColumnNotFoundError for unknown names
        resolved.append(name)
    return resolved


def _rebuild(table: Table, headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> Table:
    return Table(list(headers), rows)


def strip_whitespace(table: Table, columns: Optional[Sequence[str]] = None) -> Table:
    """Trim leading/trailing whitespace from string cells."""
    targets = set(_resolve(table, columns))
    rows = [
        [value.strip() if isinstance(value, str) and name in targets else value
         for name, value in zip(table.headers, row)]
        for row in table.rows
    ]
    return _rebuild(table, table.headers, rows)


def drop_empty_rows(table: Table) -> Table:
    """Drop rows whose cells are all missing."""
    rows = [row for row in table.rows if not all(is_missing(cell) for cell in row)]
    return _rebuild(table, table.headers, rows)


def drop_duplicates(
    table: Table,
    subset: Optional[Sequence[str]] = None,
    *,
    keep: Union[str, bool] = "first",
) -> Table:
    """Drop duplicate rows.

    *keep* may be ``"first"``, ``"last"`` or ``False`` (drop all duplicates).
    """
    if keep not in ("first", "last", False):
        raise ValueError("keep must be 'first', 'last' or False")
    headers = table.headers
    keys = _resolve(table, subset) if subset is not None else headers
    indices = [headers.index(name) for name in keys]

    rows = table.rows
    seen: dict = {}
    for position, row in enumerate(rows):
        signature = tuple(row[i] for i in indices)
        seen.setdefault(signature, []).append(position)

    if keep == "first":
        chosen = {positions[0] for positions in seen.values()}
    elif keep == "last":
        chosen = {positions[-1] for positions in seen.values()}
    else:
        chosen = {positions[0] for positions in seen.values() if len(positions) == 1}
    return _rebuild(table, headers, [row for i, row in enumerate(rows) if i in chosen])


def drop_missing(
    table: Table,
    columns: Optional[Sequence[str]] = None,
    *,
    how: str = "any",
    threshold: Optional[Union[int, float]] = None,
) -> Table:
    """Drop rows containing missing values.

    With ``how="any"`` a row is dropped when *any* selected column is missing;
    with ``how="all"`` only when *every* selected column is missing.  When
    *threshold* is given it overrides *how*: an ``int`` requires that many
    non-missing values, a float in ``(0, 1]`` requires that fraction.
    """
    headers = table.headers
    selected = _resolve(table, columns)
    indices = [headers.index(name) for name in selected]

    if threshold is not None:
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise TypeError("threshold must be an int or float")
        if isinstance(threshold, float):
            if not 0 < threshold <= 1:
                raise ValueError("float threshold must be in (0, 1]")
            required = threshold * len(indices)
        else:
            if threshold < 0:
                raise ValueError("int threshold must be non-negative")
            required = threshold
    elif how == "any":
        required = len(indices)
    elif how == "all":
        required = 1
    else:
        raise ValueError("how must be 'any' or 'all'")

    rows = [
        row
        for row in table.rows
        if sum(1 for i in indices if not is_missing(row[i])) >= required
    ]
    return _rebuild(table, headers, rows)


def _fill_value(values: List[Any], strategy: str, fallback: Any) -> Any:
    numbers = [n for n in (to_number(v) for v in values) if n is not None]
    if strategy == "zero":
        return 0
    if strategy == "mean":
        return statistics.fmean(numbers) if numbers else fallback
    if strategy == "median":
        return statistics.median(numbers) if numbers else fallback
    if strategy == "mode":
        present = [v for v in values if not is_missing(v)]
        if not present:
            return fallback
        return Counter(present).most_common(1)[0][0]
    raise ValueError(f"unknown strategy: {strategy!r}")


def fill_missing(
    table: Table,
    value: Any = None,
    *,
    columns: Optional[Sequence[str]] = None,
    strategy: Optional[str] = None,
) -> Table:
    """Replace missing values.

    Use *value* for a constant fill, or *strategy* (``"mean"``, ``"median"``,
    ``"mode"`` or ``"zero"``) to compute a fill per column.
    """
    if strategy is not None and strategy not in ("mean", "median", "mode", "zero"):
        raise ValueError(f"unknown strategy: {strategy!r}")

    headers = table.headers
    targets = set(_resolve(table, columns))
    fills: dict[str, Any] = {}
    for name in targets:
        if strategy is None:
            fills[name] = value
        else:
            column_values = list(table.column(name))
            fills[name] = _fill_value(column_values, strategy, value)

    rows = [
        [fills[name] if name in targets and is_missing(cell) else cell
         for name, cell in zip(headers, row)]
        for row in table.rows
    ]
    return _rebuild(table, headers, rows)


def rename_columns(table: Table, mapping: Mapping[str, str]) -> Table:
    """Return a table with columns renamed according to *mapping*."""
    for name in mapping:
        table.column(name)  # validate source names
    headers = [mapping.get(name, name) for name in table.headers]
    return _rebuild(table, headers, table.rows)


def drop_columns(table: Table, columns: Union[str, Sequence[str]]) -> Table:
    """Return a table without *columns*."""
    if isinstance(columns, str):
        columns = [columns]
    for name in columns:
        table.column(name)  # validate
    drop = set(columns)
    headers = [name for name in table.headers if name not in drop]
    if not headers:
        raise ValueError("cannot drop every column")
    indices = [table.headers.index(name) for name in headers]
    rows = [[row[i] for i in indices] for row in table.rows]
    return _rebuild(table, headers, rows)


def replace_values(
    table: Table,
    replacements: Union[Mapping[Any, Any], Callable[[Any], Any]],
    columns: Optional[Sequence[str]] = None,
) -> Table:
    """Replace cell values, either via a mapping or a callable."""
    headers = table.headers
    targets = set(_resolve(table, columns))

    def convert(cell: Any) -> Any:
        if isinstance(replacements, Mapping):
            return replacements.get(cell, cell)
        return replacements(cell)

    rows = [
        [convert(cell) if name in targets else cell for name, cell in zip(headers, row)]
        for row in table.rows
    ]
    return _rebuild(table, headers, rows)


def convert_types(
    table: Table,
    converters: Mapping[str, Callable[[Any], Any]],
    *,
    on_error: str = "none",
) -> Table:
    """Apply *converters* (column name -> callable) to each cell.

    When a converter raises, *on_error* controls the result: ``"none"`` stores
    ``None``, ``"keep"`` retains the original value and ``"raise"`` re-raises.
    """
    if on_error not in ("none", "keep", "raise"):
        raise ValueError("on_error must be 'none', 'keep' or 'raise'")
    for name in converters:
        table.column(name)  # validate

    headers = table.headers

    def convert(name: str, cell: Any) -> Any:
        converter = converters[name]
        try:
            return converter(cell)
        except (TypeError, ValueError):
            if on_error == "raise":
                raise
            return None if on_error == "none" else cell

    rows = [
        [convert(name, cell) if name in converters else cell
         for name, cell in zip(headers, row)]
        for row in table.rows
    ]
    return _rebuild(table, headers, rows)


def coerce_numeric(table: Table, columns: Optional[Sequence[str]] = None) -> Table:
    """Convert selected columns to numbers, storing ``None`` on failure."""
    targets = _resolve(table, columns)
    return convert_types(table, {name: to_number for name in targets}, on_error="none")
