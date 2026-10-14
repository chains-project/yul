"""Cleaning operations. Each function takes a Table and returns a new Table."""

from __future__ import annotations

import re
import statistics
from typing import Any, Callable, Iterable, Literal

from ._util import is_missing as _is_missing, is_numeric as _is_numeric
from .loader import infer_type, parse_value
from .table import Table


def _resolve(table: Table, columns: Iterable[str] | None) -> list[str]:
    cols = list(table.columns if columns is None else columns)
    for c in cols:
        if c not in table.columns:
            raise KeyError(c)
    return cols


def snake_case(name: str) -> str:
    """'First Name' -> 'first_name', 'totalAmount($)' -> 'total_amount'."""
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name.strip())
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return name or "column"


def normalize_column_names(table: Table) -> Table:
    """Convert column names to unique snake_case identifiers."""
    seen: set[str] = set()
    mapping = {}
    for col in table.columns:
        base = candidate = snake_case(col)
        n = 2
        while candidate in seen:
            candidate = f"{base}_{n}"
            n += 1
        seen.add(candidate)
        mapping[col] = candidate
    return table.rename(mapping)


def strip_whitespace(table: Table, columns: Iterable[str] | None = None) -> Table:
    """Strip leading/trailing whitespace from string values; empty strings become None."""
    idxs = {table.columns.index(c) for c in _resolve(table, columns)}

    def clean(i: int, v: Any) -> Any:
        if i in idxs and isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    return Table(table.columns, ([clean(i, v) for i, v in enumerate(row)] for row in table.rows))


def drop_missing(
    table: Table,
    columns: Iterable[str] | None = None,
    how: Literal["any", "all"] = "any",
) -> Table:
    """Drop rows with missing values in ``columns`` (default: all columns).

    ``how='any'`` drops a row if any of those values is missing; ``how='all'``
    only if every one of them is.
    """
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    idxs = [table.columns.index(c) for c in _resolve(table, columns)]
    test = any if how == "any" else all
    return Table(table.columns, (r for r in table.rows if not test(_is_missing(r[i]) for i in idxs)))


def drop_empty_columns(table: Table) -> Table:
    """Remove columns where every value is missing."""
    keep = [c for c in table.columns if not all(_is_missing(v) for v in table.column(c))]
    return table.select(*keep)


FillStrategy = Literal["mean", "median", "mode", "ffill", "bfill"]


def fill_missing(
    table: Table,
    value: Any = None,
    *,
    strategy: FillStrategy | None = None,
    columns: Iterable[str] | None = None,
) -> Table:
    """Fill missing values with a constant, a per-column dict, or a strategy.

    Exactly one of ``value`` or ``strategy`` must be given. ``value`` may be a
    dict mapping column name to fill value. Strategies:

    - ``mean`` / ``median``: numeric columns only (others are left unchanged
      when ``columns`` is not given, and raise ``TypeError`` if named).
    - ``mode``: most common value (first seen wins ties).
    - ``ffill`` / ``bfill``: propagate the previous / next present value.
    """
    if (value is None) == (strategy is None):
        raise ValueError("specify exactly one of value or strategy")
    explicit = columns is not None
    if isinstance(value, dict):
        cols = _resolve(table, value.keys())
    else:
        cols = _resolve(table, columns)

    result = table
    for col in cols:
        values = result.column(col)
        if strategy is None:
            fill = value[col] if isinstance(value, dict) else value
            new = [fill if _is_missing(v) else v for v in values]
        elif strategy in ("ffill", "bfill"):
            new = _propagate(values, reverse=strategy == "bfill")
        else:
            present = [v for v in values if not _is_missing(v)]
            if not present:
                continue
            if strategy == "mode":
                fill = statistics.mode(present)
            else:
                if not _is_numeric(present):
                    if explicit:
                        raise TypeError(f"column {col!r} is not numeric; cannot use {strategy}")
                    continue
                agg: Callable[[list[Any]], Any] = statistics.fmean if strategy == "mean" else statistics.median
                fill = agg(present)
            new = [fill if _is_missing(v) else v for v in values]
        result = result.with_column(col, new)
    return result


def _propagate(values: list[Any], reverse: bool) -> list[Any]:
    seq = values[::-1] if reverse else list(values)
    last = None
    for i, v in enumerate(seq):
        if _is_missing(v):
            seq[i] = last
        else:
            last = v
    return seq[::-1] if reverse else seq


def drop_duplicates(table: Table, columns: Iterable[str] | None = None, keep: Literal["first", "last"] = "first") -> Table:
    """Remove duplicate rows, comparing only ``columns`` if given."""
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")
    idxs = [table.columns.index(c) for c in _resolve(table, columns)]
    rows = table.rows if keep == "first" else table.rows[::-1]
    seen: set[tuple[Any, ...]] = set()
    out = []
    for r in rows:
        key = tuple(r[i] for i in idxs)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return Table(table.columns, out if keep == "first" else out[::-1])


def convert_types(table: Table, dtypes: dict[str, str], errors: Literal["raise", "coerce"] = "raise") -> Table:
    """Convert columns to 'int', 'float', 'bool' or 'str'.

    With ``errors='coerce'``, values that fail to convert become ``None``.
    """
    if errors not in ("raise", "coerce"):
        raise ValueError("errors must be 'raise' or 'coerce'")
    result = table
    for col, t in dtypes.items():
        new = []
        for v in result.column(col):
            if _is_missing(v):
                new.append(None)
            else:
                try:
                    new.append(_convert(v, t))
                except ValueError:
                    if errors == "raise":
                        raise ValueError(f"column {col!r}: cannot convert {v!r} to {t}") from None
                    new.append(None)
        result = result.with_column(col, new)
    return result


def _convert(v: Any, t: str) -> Any:
    if t == "str":
        return str(v)
    if isinstance(v, str):
        return parse_value(v.strip(), t)
    if t == "int":
        if isinstance(v, float) and not v.is_integer():
            raise ValueError(v)
        return int(v)
    if t == "float":
        return float(v)
    if t == "bool":
        if v in (0, 1):
            return bool(v)
        raise ValueError(v)
    raise ValueError(f"unknown type {t!r}")


def infer_types(table: Table) -> Table:
    """Re-run type inference on string columns (e.g. after stripping whitespace)."""
    dtypes = {}
    for col in table.columns:
        values = [v for v in table.column(col) if v is not None]
        if values and all(isinstance(v, str) for v in values):
            t = infer_type(v.strip() for v in values)
            if t != "str":
                dtypes[col] = t
    return convert_types(table, dtypes)


def remove_outliers(table: Table, column: str, method: Literal["iqr", "zscore"] = "iqr", threshold: float | None = None) -> Table:
    """Drop rows whose numeric ``column`` value is an outlier.

    ``iqr``: outside [Q1 - k*IQR, Q3 + k*IQR], k defaults to 1.5.
    ``zscore``: |z| > threshold, default 3.0.
    Rows with a missing value in ``column`` are kept.
    """
    idx = table.columns.index(_resolve(table, [column])[0])
    values = [r[idx] for r in table.rows if not _is_missing(r[idx])]
    if not _is_numeric(values):
        raise TypeError(f"column {column!r} is not numeric")
    if len(values) < 2:
        return table
    if method == "iqr":
        k = 1.5 if threshold is None else threshold
        q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
        lo, hi = q1 - k * (q3 - q1), q3 + k * (q3 - q1)
    elif method == "zscore":
        k = 3.0 if threshold is None else threshold
        mean, sd = statistics.fmean(values), statistics.stdev(values)
        if sd == 0:
            return table
        lo, hi = mean - k * sd, mean + k * sd
    else:
        raise ValueError("method must be 'iqr' or 'zscore'")
    return Table(table.columns, (r for r in table.rows if _is_missing(r[idx]) or lo <= r[idx] <= hi))


def clean(table: Table) -> Table:
    """Apply a sensible default pipeline.

    Normalize column names, strip whitespace, re-infer types, drop fully
    empty rows/columns, and drop exact duplicate rows.
    """
    t = normalize_column_names(table)
    t = strip_whitespace(t)
    t = infer_types(t)
    t = drop_empty_columns(t)
    if t.columns:
        t = drop_missing(t, how="all")
    return drop_duplicates(t)
