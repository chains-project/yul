"""Data-cleaning transformations. Every function returns a new Table."""

from __future__ import annotations

import re
import statistics
from typing import Any, Callable, Literal, Mapping, Sequence

from .io import infer_column
from .table import Table


def normalize_column_names(table: Table) -> Table:
    """Convert headers to snake_case: ``" Unit Price ($)"`` -> ``"unit_price"``."""
    mapping = {}
    for name in table.columns:
        snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name.strip())
        snake = re.sub(r"[^0-9a-zA-Z]+", "_", snake).strip("_").lower()
        mapping[name] = snake or name
    if len(set(mapping.values())) != len(mapping):
        raise ValueError(f"normalized column names collide: {mapping}")
    return table.rename(mapping)


def strip_whitespace(table: Table, columns: Sequence[str] | None = None) -> Table:
    """Trim and collapse internal runs of whitespace in string cells."""
    def clean(value: Any) -> Any:
        return " ".join(value.split()) if isinstance(value, str) else value
    return _map_columns(table, clean, columns)


def drop_duplicates(table: Table, subset: Sequence[str] | None = None,
                    keep: Literal["first", "last"] = "first") -> Table:
    """Remove duplicate rows, comparing only ``subset`` columns if given."""
    keys = list(subset) if subset is not None else table.columns
    cols = [table[k] for k in keys]
    order = range(len(table)) if keep == "first" else range(len(table) - 1, -1, -1)
    seen: set[tuple] = set()
    kept = []
    for i in order:
        key = tuple(_hashable(c[i]) for c in cols)
        if key not in seen:
            seen.add(key)
            kept.append(i)
    return table.take(sorted(kept))


def drop_missing(table: Table, subset: Sequence[str] | None = None,
                 how: Literal["any", "all"] = "any") -> Table:
    """Drop rows with missing values in ``subset`` (all columns by default)."""
    keys = list(subset) if subset is not None else table.columns
    test = any if how == "any" else all
    return table.filter(lambda row: not test(row[k] is None for k in keys))


def drop_empty_columns(table: Table, threshold: float = 1.0) -> Table:
    """Drop columns whose fraction of missing values is >= ``threshold``."""
    if not len(table):
        return table
    drop = [c for c in table.columns
            if table[c].count(None) / len(table) >= threshold]
    return table.drop(drop)


FillStrategy = Literal["mean", "median", "mode", "ffill", "bfill"]


def fill_missing(table: Table,
                 value: Any | Mapping[str, Any] = None,
                 strategy: FillStrategy | None = None,
                 columns: Sequence[str] | None = None) -> Table:
    """Replace missing values.

    Either pass a constant ``value`` (or a ``{column: value}`` mapping), or a
    ``strategy``: ``"mean"``/``"median"`` (numeric columns only), ``"mode"``,
    ``"ffill"`` (carry last seen value forward) or ``"bfill"``.
    """
    if (value is None) == (strategy is None):
        raise ValueError("pass exactly one of 'value' or 'strategy'")
    targets = list(columns) if columns is not None else table.columns
    if isinstance(value, Mapping):
        targets = [c for c in targets if c in value]

    result = table
    for name in targets:
        values = table[name]
        if strategy is None:
            fill = value[name] if isinstance(value, Mapping) else value
            values = [fill if v is None else v for v in values]
        elif strategy in ("ffill", "bfill"):
            values = _propagate(values, reverse=strategy == "bfill")
        else:
            present = [v for v in values if v is not None]
            if not present:
                continue
            if strategy == "mode":
                fill = statistics.mode(present)
            elif not all(_is_number(v) for v in present):
                if columns is not None:
                    raise TypeError(f"column {name!r} is not numeric")
                continue  # silently skip non-numeric columns when not targeted
            elif strategy == "mean":
                fill = statistics.fmean(present)
            elif strategy == "median":
                fill = statistics.median(present)
            else:
                raise ValueError(f"unknown strategy: {strategy!r}")
            values = [fill if v is None else v for v in values]
        result = result.with_column(name, values)
    return result


def convert_types(table: Table, types: Mapping[str, type | Callable[[Any], Any]],
                  errors: Literal["raise", "coerce"] = "raise") -> Table:
    """Convert columns with the given callables, e.g. ``{"age": int}``.

    With ``errors="coerce"``, values that fail to convert become ``None``.
    """
    result = table
    for name, converter in types.items():
        converted = []
        for v in table[name]:
            if v is None:
                converted.append(None)
                continue
            try:
                converted.append(converter(v))
            except (ValueError, TypeError):
                if errors == "raise":
                    raise
                converted.append(None)
        result = result.with_column(name, converted)
    return result


def infer_types(table: Table, columns: Sequence[str] | None = None) -> Table:
    """Re-run CSV type inference on string columns (e.g. after cleaning)."""
    result = table
    for name in columns if columns is not None else table.columns:
        values = table[name]
        if all(v is None or isinstance(v, str) for v in values):
            result = result.with_column(name, infer_column(values)[1])
    return result


def replace_values(table: Table, mapping: Mapping[Any, Any],
                   columns: Sequence[str] | None = None) -> Table:
    """Replace exact cell values, e.g. ``{"M": "male", "F": "female"}``."""
    return _map_columns(
        table, lambda v: mapping.get(v, v) if _is_hashable(v) else v, columns)


def remove_outliers(table: Table, column: str, method: Literal["iqr", "zscore"] = "iqr",
                    factor: float | None = None) -> Table:
    """Drop rows whose ``column`` value is an outlier.

    ``"iqr"`` removes values outside ``[Q1 - k*IQR, Q3 + k*IQR]`` (k=1.5 by
    default); ``"zscore"`` removes values more than ``k`` standard deviations
    from the mean (k=3 by default). Rows with a missing value are kept.
    """
    values = [v for v in table[column] if v is not None]
    if len(values) < 2:
        return table
    if method == "iqr":
        k = 1.5 if factor is None else factor
        q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
        low, high = q1 - k * (q3 - q1), q3 + k * (q3 - q1)
    elif method == "zscore":
        k = 3.0 if factor is None else factor
        mean, std = statistics.fmean(values), statistics.stdev(values)
        low, high = mean - k * std, mean + k * std
    else:
        raise ValueError(f"unknown method: {method!r}")
    return table.filter(lambda row: row[column] is None or low <= row[column] <= high)


def clean(table: Table) -> Table:
    """Apply a sensible default pipeline.

    Normalizes column names, trims whitespace, drops fully empty rows and
    columns, removes exact duplicate rows, and re-infers column types.
    """
    table = normalize_column_names(table)
    table = strip_whitespace(table)
    table = replace_values(table, {"": None})
    table = drop_empty_columns(table)
    table = drop_missing(table, how="all")
    table = drop_duplicates(table)
    return infer_types(table)


def _map_columns(table: Table, func: Callable[[Any], Any],
                 columns: Sequence[str] | None) -> Table:
    result = table
    for name in columns if columns is not None else table.columns:
        result = result.with_column(name, [func(v) for v in table[name]])
    return result


def _propagate(values: list[Any], reverse: bool) -> list[Any]:
    out = list(reversed(values)) if reverse else list(values)
    last = None
    for i, v in enumerate(out):
        if v is None:
            out[i] = last
        else:
            last = v
    return out[::-1] if reverse else out


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_hashable(value: Any) -> bool:
    try:
        hash(value)
    except TypeError:
        return False
    return True


def _hashable(value: Any) -> Any:
    return value if _is_hashable(value) else repr(value)
