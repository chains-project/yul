"""Summary statistics and simple analytics for tables."""

from __future__ import annotations

import math
import statistics
from collections import Counter

from .cleaning import infer_dtype
from .errors import AnalysisError
from .table import Table
from .values import is_missing


def effective_dtypes(table):
    """Return each column's declared dtype, inferring any ``"str"`` columns."""
    result = {}
    for column in table.columns:
        dtype = table.dtypes.get(column, "str")
        if dtype == "str":
            dtype = infer_dtype(table[column])
        result[column] = dtype
    return result


def _numbers(values):
    numbers = []
    for value in values:
        try:
            numbers.append(float(value))
        except (TypeError, ValueError):
            continue
    return numbers


def _hashable(value):
    if isinstance(value, (list, dict, set)):
        return repr(value)
    return value


def numeric_columns(table):
    """Return the names of columns that hold numeric data."""
    dtypes = effective_dtypes(table)
    return [c for c in table.columns if dtypes[c] in ("int", "float")]


def describe(table):
    """Return a new :class:`Table` of per-column summary statistics."""
    records = []
    dtypes = effective_dtypes(table)
    for column in table.columns:
        values = table[column]
        present = [value for value in values if not is_missing(value)]
        dtype = dtypes[column]
        numbers = _numbers(present) if dtype in ("int", "float") else []
        record = {
            "column": column,
            "dtype": dtype,
            "count": len(present),
            "missing": len(values) - len(present),
            "unique": len({_hashable(v) for v in present}),
            "mean": statistics.fmean(numbers) if numbers else None,
            "median": statistics.median(numbers) if numbers else None,
            "stdev": statistics.stdev(numbers) if len(numbers) > 1 else None,
            "min": min(numbers) if numbers else _extreme(present, min),
            "max": max(numbers) if numbers else _extreme(present, max),
        }
        records.append(record)
    columns = [
        "column",
        "dtype",
        "count",
        "missing",
        "unique",
        "mean",
        "median",
        "stdev",
        "min",
        "max",
    ]
    return Table.from_dicts(records, columns=columns)


def _extreme(values, selector):
    if not values:
        return None
    try:
        return selector(values)
    except TypeError:
        return None


def value_counts(table, column, normalize=False, limit=None):
    """Count occurrences of each distinct value in *column*."""
    values = table[column]
    counts = Counter(_hashable(value) for value in values)
    total = sum(counts.values())
    ordered = counts.most_common(limit)
    records = []
    for value, count in ordered:
        record = {"value": value, "count": count}
        if normalize:
            record["proportion"] = count / total if total else None
        records.append(record)
    columns = ["value", "count"] + (["proportion"] if normalize else [])
    return Table.from_dicts(records, columns=columns)


def correlation(table, column_a, column_b):
    """Return the Pearson correlation coefficient between two columns."""
    pairs = [
        (a, b)
        for a, b in zip(table[column_a], table[column_b])
        if not is_missing(a) and not is_missing(b)
    ]
    if len(pairs) < 2:
        raise AnalysisError("at least two complete pairs are required")
    xs = _numbers([pair[0] for pair in pairs])
    ys = _numbers([pair[1] for pair in pairs])
    if len(xs) != len(pairs) or len(ys) != len(pairs):
        raise AnalysisError("both columns must be numeric")
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    variance_x = sum((x - mean_x) ** 2 for x in xs)
    variance_y = sum((y - mean_y) ** 2 for y in ys)
    denominator = math.sqrt(variance_x * variance_y)
    if denominator == 0:
        raise AnalysisError("correlation is undefined for zero-variance input")
    return covariance / denominator


def aggregate(table, by, aggregations):
    """Group rows by *by* and compute *aggregations*.

    *aggregations* maps a result column name to ``(source_column, func)``
    where *func* is ``"count"``, ``"sum"``, ``"mean"``, ``"min"`` or
    ``"max"`` (or any callable accepting the list of non-missing values).
    """
    if isinstance(by, str):
        by = [by]
    positions = [table.index(column) for column in by]
    groups = {}
    for row in table.rows:
        key = tuple(row[position] for position in positions)
        groups.setdefault(key, []).append(row)

    records = []
    for key, rows in groups.items():
        record = {column: value for column, value in zip(by, key)}
        for name, (source, func) in aggregations.items():
            position = table.index(source)
            values = [row[position] for row in rows if not is_missing(row[position])]
            record[name] = _apply_aggregation(func, values)
        records.append(record)
    columns = list(by) + list(aggregations)
    return Table.from_dicts(records, columns=columns)


def _apply_aggregation(func, values):
    if callable(func):
        return func(values)
    if func == "count":
        return len(values)
    if func == "sum":
        return sum(_numbers(values))
    if func == "mean":
        numbers = _numbers(values)
        return statistics.fmean(numbers) if numbers else None
    if func == "min":
        return min(values) if values else None
    if func == "max":
        return max(values) if values else None
    raise AnalysisError(f"unsupported aggregation: {func!r}")


def summary(table):
    """Return a compact dictionary describing *table*."""
    missing = sum(
        1
        for row in table.rows
        for value in row
        if is_missing(value)
    )
    return {
        "rows": len(table.rows),
        "columns": len(table.columns),
        "missing_cells": missing,
        "dtypes": effective_dtypes(table),
    }
