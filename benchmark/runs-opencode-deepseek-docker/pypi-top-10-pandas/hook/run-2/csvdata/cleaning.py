"""Cleaning and type-coercion operations for :class:`~csvdata.table.Table`."""

from __future__ import annotations

import statistics
from collections import Counter

from .errors import CleaningError
from .table import Table
from .values import coerce_value, is_missing, looks_like_bool, looks_like_float, looks_like_int

FILL_STRATEGIES = ("drop", "constant", "mean", "median", "mode", "ffill")


def _column_list(columns):
    if columns is None:
        return None
    if isinstance(columns, str):
        return [columns]
    return list(columns)


def strip_whitespace(table):
    """Return a copy of *table* with surrounding whitespace removed from strings."""
    rows = [
        [value.strip() if isinstance(value, str) else value for value in row]
        for row in table.rows
    ]
    return Table(table.columns, rows, table.dtypes)


def infer_dtype(values):
    """Infer the most specific dtype able to represent *values*."""
    present = [value for value in values if not is_missing(value)]
    if not present:
        return "str"
    if all(isinstance(value, bool) for value in present):
        return "bool"
    if all(looks_like_bool(value) for value in present):
        return "bool"
    if all(looks_like_int(value) for value in present):
        return "int"
    if all(looks_like_float(value) for value in present):
        return "float"
    return "str"


def coerce_types(table, columns=None):
    """Infer and apply a dtype to each column, returning a new table."""
    targets = _column_list(columns) or list(table.columns)
    for column in targets:
        table.index(column)
    dtypes = dict(table.dtypes)
    for column in targets:
        dtypes[column] = infer_dtype(table[column])
    try:
        rows = [
            [
                coerce_value(value, dtypes[column])
                for column, value in zip(table.columns, row)
            ]
            for row in table.rows
        ]
    except (TypeError, ValueError) as exc:
        raise CleaningError(f"could not coerce column types: {exc}") from exc
    return Table(table.columns, rows, dtypes)


def drop_empty_rows(table):
    """Drop rows in which every value is missing."""
    rows = [row for row in table.rows if any(not is_missing(v) for v in row)]
    return Table(table.columns, rows, table.dtypes)


def drop_duplicates(table, subset=None):
    """Drop duplicate rows, optionally considering only *subset* columns."""
    if subset is None:
        positions = range(len(table.columns))
    else:
        subset = _column_list(subset)
        positions = [table.index(column) for column in subset]
    seen = set()
    rows = []
    for row in table.rows:
        key = tuple(row[position] for position in positions)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return Table(table.columns, rows, table.dtypes)


def drop_missing(table, subset=None, how="any"):
    """Drop rows containing missing values in *subset* (or all columns)."""
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    columns = [subset] if isinstance(subset, str) else (subset or table.columns)
    positions = [table.index(column) for column in columns]
    rows = []
    for row in table.rows:
        missing = [is_missing(row[position]) for position in positions]
        drop = any(missing) if how == "any" else all(missing)
        if not drop:
            rows.append(row)
    return Table(table.columns, rows, table.dtypes)


def _mode(values):
    counter = Counter(values)
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def _fill_value(table, column, strategy, value, present):
    if strategy == "constant":
        return value
    dtype = table.dtypes.get(column, "str")
    numeric = dtype in ("int", "float")
    numbers = []
    if numeric:
        numbers = [float(v) for v in present]
    if strategy == "mean" and numbers:
        return statistics.fmean(numbers)
    if strategy == "median" and numbers:
        return statistics.median(numbers)
    if strategy == "mode":
        return _mode(present)
    if strategy in ("mean", "median"):
        return _mode(present)
    raise CleaningError(f"unknown fill strategy: {strategy!r}")


def fill_missing(table, strategy="mean", value=None, columns=None):
    """Fill missing values using an imputation *strategy*."""
    if strategy not in FILL_STRATEGIES:
        raise ValueError(
            f"strategy must be one of {FILL_STRATEGIES}, got {strategy!r}"
        )
    targets = _column_list(columns) or list(table.columns)
    for column in targets:
        table.index(column)
    if strategy == "drop":
        return drop_missing(table, subset=targets, how="any")

    rows = [list(row) for row in table.rows]
    dtypes = dict(table.dtypes)
    if strategy == "ffill":
        for position, column in enumerate(table.columns):
            if column not in targets:
                continue
            last = None
            for row in rows:
                if is_missing(row[position]):
                    row[position] = last
                else:
                    last = row[position]
        return Table(table.columns, rows, dtypes)

    for column in targets:
        position = table.index(column)
        present = [row[position] for row in rows if not is_missing(row[position])]
        fill = _fill_value(table, column, strategy, value, present)
        for row in rows:
            if is_missing(row[position]):
                row[position] = fill
        if strategy in ("mean", "median") and dtypes.get(column) == "int":
            if fill is not None and not float(fill).is_integer():
                dtypes[column] = "float"
    return Table(table.columns, rows, dtypes)


def clean(
    table,
    *,
    strip=True,
    drop_empty=True,
    dedupe=False,
    subset=None,
    coerce=True,
    missing=None,
    value=None,
    columns=None,
):
    """Run a configurable cleaning pipeline over *table*.

    ``missing`` selects an imputation strategy from
    :data:`FILL_STRATEGIES` (or ``None`` to leave missing values in place).
    """
    result = table
    if strip:
        result = strip_whitespace(result)
    if drop_empty:
        result = drop_empty_rows(result)
    if coerce:
        result = coerce_types(result)
    if dedupe:
        result = drop_duplicates(result, subset=subset)
    if missing is not None:
        result = fill_missing(result, strategy=missing, value=value, columns=columns)
    return result


__all__ = [
    "FILL_STRATEGIES",
    "clean",
    "coerce_types",
    "drop_duplicates",
    "drop_empty_rows",
    "drop_missing",
    "fill_missing",
    "infer_dtype",
    "strip_whitespace",
]
