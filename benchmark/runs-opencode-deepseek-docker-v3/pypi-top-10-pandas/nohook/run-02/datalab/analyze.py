"""Analysis helpers for :mod:`datalab`."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Union

from .table import Column, Table, is_missing, to_number

__all__ = [
    "count",
    "value_counts",
    "numeric_values",
    "mean",
    "median",
    "stdev",
    "quantile",
    "describe",
    "correlation",
    "covariance",
    "group_by",
]


def numeric_values(column: Union[Column, Iterable[Any]]) -> List[float]:
    """Return the finite numeric values of *column*, ignoring missing/invalid."""
    values = column.values if isinstance(column, Column) else list(column)
    numbers: List[float] = []
    for value in values:
        number = to_number(value)
        if number is not None and not math.isinf(number):
            numbers.append(number)
    return numbers


def count(table: Table, column: Optional[str] = None) -> int:
    """Count non-missing values (overall, or within one column)."""
    if column is None:
        return table.height
    return table.height - table.column(column).missing_count()


def mean(column: Union[Column, Iterable[Any]]) -> Optional[float]:
    numbers = numeric_values(column)
    return statistics.fmean(numbers) if numbers else None


def median(column: Union[Column, Iterable[Any]]) -> Optional[float]:
    numbers = numeric_values(column)
    return statistics.median(numbers) if numbers else None


def stdev(column: Union[Column, Iterable[Any]]) -> Optional[float]:
    numbers = numeric_values(column)
    return statistics.stdev(numbers) if len(numbers) >= 2 else None


def quantile(column: Union[Column, Iterable[Any]], q: float) -> Optional[float]:
    """Return the *q* quantile (0-1) using linear interpolation."""
    if not 0 <= q <= 1:
        raise ValueError("q must be between 0 and 1")
    numbers = sorted(numeric_values(column))
    if not numbers:
        return None
    if len(numbers) == 1:
        return numbers[0]
    position = q * (len(numbers) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return numbers[int(position)]
    fraction = position - lower
    return numbers[lower] * (1 - fraction) + numbers[upper] * fraction


def value_counts(
    table: Table,
    column: str,
    *,
    normalize: bool = False,
    sort: bool = True,
) -> Dict[Any, Union[int, float]]:
    """Count occurrences of each value in *column*."""
    counter = Counter(
        value for value in table.column(column) if not is_missing(value)
    )
    if normalize:
        total = sum(counter.values())
        result: Dict[Any, Union[int, float]] = {
            key: value / total for key, value in counter.items()
        }
    else:
        result = dict(counter)
    if sort:
        return dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    return result


def describe(
    table: Table, columns: Optional[Sequence[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """Return summary statistics for each requested column.

    Every entry includes ``count``, ``missing`` and ``unique``.  Numeric
    columns additionally report ``mean``, ``median``, ``stdev``, ``min``,
    ``max``, ``q1`` and ``q3``; other columns report ``top`` and ``freq``.
    """
    names = table.headers if columns is None else list(columns)
    summary: Dict[str, Dict[str, Any]] = {}
    for name in names:
        column = table.column(name)
        values = list(column)
        present = [value for value in values if not is_missing(value)]
        stats: Dict[str, Any] = {
            "count": len(present),
            "missing": len(values) - len(present),
            "unique": len(set(present)),
        }
        numbers = numeric_values(values)
        if numbers and len(numbers) == len(present):
            stats.update(
                {
                    "mean": statistics.fmean(numbers),
                    "median": statistics.median(numbers),
                    "stdev": stdev(numbers),
                    "min": min(numbers),
                    "max": max(numbers),
                    "q1": quantile(numbers, 0.25),
                    "q3": quantile(numbers, 0.75),
                }
            )
        elif present:
            top, freq = Counter(present).most_common(1)[0]
            stats.update({"top": top, "freq": freq})
        summary[name] = stats
    return summary


def _numeric_pairs(table: Table, x: str, y: str) -> List[tuple]:
    x_values = list(table.column(x))
    y_values = list(table.column(y))
    pairs = []
    for raw_x, raw_y in zip(x_values, y_values):
        nx, ny = to_number(raw_x), to_number(raw_y)
        if nx is not None and ny is not None:
            pairs.append((nx, ny))
    return pairs


def covariance(table: Table, x: str, y: str) -> Optional[float]:
    """Return the sample covariance of columns *x* and *y*."""
    pairs = _numeric_pairs(table, x, y)
    if len(pairs) < 2:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    return sum((a - mean_x) * (b - mean_y) for a, b in pairs) / (len(pairs) - 1)


def correlation(table: Table, x: str, y: str) -> Optional[float]:
    """Return the Pearson correlation coefficient of columns *x* and *y*."""
    pairs = _numeric_pairs(table, x, y)
    if len(pairs) < 2:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in pairs)
    denom_x = math.sqrt(sum((a - mean_x) ** 2 for a in xs))
    denom_y = math.sqrt(sum((b - mean_y) ** 2 for b in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def _aggregate(values: List[Any], func: Union[str, Callable]) -> Any:
    present = [value for value in values if not is_missing(value)]
    if callable(func):
        return func(present)
    numbers = numeric_values(values)
    if func == "count":
        return len(present)
    if func == "sum":
        return sum(numbers) if numbers else 0
    if func == "mean":
        return statistics.fmean(numbers) if numbers else None
    if func == "median":
        return statistics.median(numbers) if numbers else None
    if func == "stdev":
        return statistics.stdev(numbers) if len(numbers) >= 2 else None
    if func == "min":
        return min(numbers) if numbers else (min(map(str, present)) if present else None)
    if func == "max":
        return max(numbers) if numbers else (max(map(str, present)) if present else None)
    raise ValueError(f"unknown aggregation: {func!r}")


def _agg_name(func: Union[str, Callable]) -> str:
    if isinstance(func, str):
        return func
    return getattr(func, "__name__", "agg")


def group_by(
    table: Table,
    by: Union[str, Sequence[str]],
    aggregations: Mapping[str, Union[str, Callable, Sequence[Union[str, Callable]]]],
) -> Table:
    """Group rows by *by* and aggregate *aggregations*.

    *aggregations* maps a column name (or ``"*"`` for row counts) to one or
    more aggregation names/callables.  Aggregation names are ``sum``, ``mean``,
    ``median``, ``min``, ``max``, ``count`` and ``stdev``.  Result columns are
    named ``<column>_<aggregation>``.

    Example
    -------
    >>> group_by(t, "region", {"sales": ["sum", "mean"], "*": "count"})
    """
    keys = [by] if isinstance(by, str) else list(by)
    for key in keys:
        table.column(key)  # validate group columns

    groups: Dict[tuple, List[List[Any]]] = {}
    order: List[tuple] = []
    key_indices = [table.headers.index(key) for key in keys]
    for row in table.rows:
        signature = tuple(row[i] for i in key_indices)
        if signature not in groups:
            groups[signature] = []
            order.append(signature)
        groups[signature].append(row)

    header_out = list(keys)
    for column, funcs in aggregations.items():
        func_list = [funcs] if isinstance(funcs, str) or callable(funcs) else list(funcs)
        for func in func_list:
            label = _agg_name(func)
            header_out.append(label if column == "*" else f"{column}_{label}")

    output_rows: List[List[Any]] = []
    for signature in order:
        rows = groups[signature]
        result = list(signature)
        for column, funcs in aggregations.items():
            func_list = [funcs] if isinstance(funcs, str) or callable(funcs) else list(funcs)
            if column == "*":
                for func in func_list:
                    if func not in ("count", "size"):
                        raise ValueError("'*' only supports the 'count'/'size' aggregations")
                    result.append(len(rows))
                continue
            index = table.headers.index(column)
            group_values = [row[index] for row in rows]
            for func in func_list:
                result.append(_aggregate(group_values, func))
        output_rows.append(result)
    return Table(header_out, output_rows)
