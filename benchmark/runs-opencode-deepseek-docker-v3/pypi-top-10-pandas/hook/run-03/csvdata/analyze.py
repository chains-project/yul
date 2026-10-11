"""Descriptive statistics and analysis for :class:`~csvdata.table.Table`."""

from __future__ import annotations

from collections import Counter
from statistics import mean, median, stdev

from .clean import _to_number
from .table import Table, is_missing


def _present_values(table: Table, column: str) -> list:
    return [v for v in table.column(column) if not is_missing(v)]


def _numeric_values(table: Table, column: str) -> list[float]:
    numbers = []
    for value in table.column(column):
        if is_missing(value) or isinstance(value, bool):
            continue
        number = _to_number(value)
        if number is not None:
            numbers.append(number)
    return numbers


def column_summary(table: Table, column: str) -> dict:
    """Return a summary dictionary describing a single *column*."""
    table.column(column)  # validate
    values = _present_values(table, column)
    summary = {
        "column": column,
        "count": len(values),
        "missing": len(table) - len(values),
        "unique": len(set(map(_hashable, values))),
    }
    numbers = _numeric_values(table, column)
    if numbers and len(numbers) == len(values):
        summary["type"] = "numeric"
        summary["min"] = min(numbers)
        summary["max"] = max(numbers)
        summary["mean"] = mean(numbers)
        summary["median"] = median(numbers)
        summary["stdev"] = stdev(numbers) if len(numbers) > 1 else None
    else:
        summary["type"] = "categorical"
        if values:
            top, freq = Counter(values).most_common(1)[0]
            summary["top"] = top
            summary["freq"] = freq
        else:
            summary["top"] = None
            summary["freq"] = 0
    return summary


def describe(table: Table, columns: list[str] | None = None) -> dict[str, dict]:
    """Summarize every column (or just *columns*) of *table*."""
    target = columns if columns is not None else table.columns
    return {name: column_summary(table, name) for name in target}


def value_counts(table: Table, column: str, limit: int | None = None) -> list[tuple]:
    """Return ``(value, count)`` pairs for *column*, most frequent first."""
    table.column(column)  # validate
    counts = Counter(_present_values(table, column))
    pairs = sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))
    return pairs[:limit] if limit is not None else pairs


def correlation(table: Table, column_a: str, column_b: str) -> float | None:
    """Return the Pearson correlation between two numeric columns.

    Returns ``None`` when fewer than two complete pairs exist or a column has
    zero variance.
    """
    pairs = []
    for row in table:
        a, b = row[column_a], row[column_b]
        if is_missing(a) or is_missing(b):
            continue
        a, b = _to_number(a), _to_number(b)
        if a is None or b is None:
            continue
        pairs.append((a, b))
    if len(pairs) < 2:
        return None

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mean_x, mean_y = mean(xs), mean(ys)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x == 0 or var_y == 0:
        return None
    return cov / (var_x**0.5 * var_y**0.5)


def _hashable(value):
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, dict):
        return tuple(sorted(value.items()))
    return value
