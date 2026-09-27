"""Descriptive statistics and grouping for :class:`~datalib.table.Table`."""

from __future__ import annotations

import math
import statistics
from typing import Any, Callable, Iterable, Mapping, Sequence

from .cleaning import is_missing
from .exceptions import DataLibError
from .table import Table


# ----------------------------------------------------------------------
# Column classification
# ----------------------------------------------------------------------
def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def numeric_columns(table: Table) -> list[str]:
    """Names of columns that contain numbers and no non-null non-numbers."""
    result = []
    for name in table.columns:
        values = [v for v in table.column(name) if not is_missing(v)]
        if values and all(_is_number(v) for v in values):
            result.append(name)
    return result


def categorical_columns(table: Table) -> list[str]:
    """Names of columns that are not numeric."""
    numeric = set(numeric_columns(table))
    return [name for name in table.columns if name not in numeric]


def _numbers(table: Table, column: str) -> list[float]:
    table._require(column)
    values = [v for v in table.column(column) if not is_missing(v)]
    for value in values:
        if not _is_number(value):
            raise DataLibError(f"column {column!r} contains non-numeric value {value!r}")
    return [float(v) for v in values]


# ----------------------------------------------------------------------
# Single-column statistics
# ----------------------------------------------------------------------
def count(table: Table, column: str) -> int:
    """Number of non-missing values in ``column``."""
    table._require(column)
    return sum(1 for v in table.column(column) if not is_missing(v))


def missing_count(table: Table, column: str) -> int:
    """Number of missing values in ``column``."""
    return len(table) - count(table, column)


def mean(table: Table, column: str) -> float:
    return statistics.fmean(_numbers(table, column))


def median(table: Table, column: str) -> float:
    return statistics.median(_numbers(table, column))


def mode(table: Table, column: str) -> Any:
    values = [v for v in table.column(column) if not is_missing(v)]
    if not values:
        raise DataLibError(f"column {column!r} has no values")
    return statistics.mode(values)


def stdev(table: Table, column: str, ddof: int = 1) -> float:
    """Standard deviation; ``ddof=1`` gives the sample statistic."""
    data = _numbers(table, column)
    if len(data) <= ddof:
        raise DataLibError("not enough values for standard deviation")
    return statistics.stdev(data) if ddof == 1 else statistics.pstdev(data)


def variance(table: Table, column: str, ddof: int = 1) -> float:
    data = _numbers(table, column)
    if len(data) <= ddof:
        raise DataLibError("not enough values for variance")
    return statistics.variance(data) if ddof == 1 else statistics.pvariance(data)


def minimum(table: Table, column: str) -> Any:
    values = [v for v in table.column(column) if not is_missing(v)]
    if not values:
        raise DataLibError(f"column {column!r} has no values")
    return min(values)


def maximum(table: Table, column: str) -> Any:
    values = [v for v in table.column(column) if not is_missing(v)]
    if not values:
        raise DataLibError(f"column {column!r} has no values")
    return max(values)


def total(table: Table, column: str) -> float:
    return math.fsum(_numbers(table, column))


def quantile(values: Sequence[float], q: float) -> float:
    """Linear-interpolated quantile of ``values`` for ``0 <= q <= 1``."""
    if not 0 <= q <= 1:
        raise DataLibError("q must be between 0 and 1")
    data = sorted(values)
    if not data:
        raise DataLibError("cannot take quantile of an empty sequence")
    if len(data) == 1:
        return data[0]
    position = (len(data) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return data[low]
    return data[low] * (high - position) + data[high] * (position - low)


def percentile(table: Table, column: str, p: float) -> float:
    """Percentile (``0..100``) of a numeric column."""
    return quantile(_numbers(table, column), p / 100.0)


# ----------------------------------------------------------------------
# Distributions and relationships
# ----------------------------------------------------------------------
def value_counts(
    table: Table,
    column: str,
    *,
    normalize: bool = False,
    dropna: bool = True,
) -> list[tuple[Any, float]]:
    """Frequency of each distinct value in ``column``, most common first."""
    table._require(column)
    counts: dict[Any, int] = {}
    for value in table.column(column):
        if is_missing(value):
            if dropna:
                continue
            key = None
        else:
            key = value
        counts[key] = counts.get(key, 0) + 1

    total_count = sum(counts.values())
    items = sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))
    if normalize:
        return [(k, c / total_count) for k, c in items]
    return [(k, c) for k, c in items]


def value_counts_table(table: Table, column: str, **kwargs: Any) -> Table:
    """Like :func:`value_counts` but returns a two-column :class:`Table`."""
    rows = value_counts(table, column, **kwargs)
    return Table([column, "count"], rows)


def covariance(a: Sequence[float], b: Sequence[float], ddof: int = 1) -> float:
    if len(a) != len(b):
        raise DataLibError("sequences must have the same length")
    if len(a) <= ddof:
        raise DataLibError("not enough values for covariance")
    mean_a = statistics.fmean(a)
    mean_b = statistics.fmean(b)
    divisor = len(a) - ddof
    return sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b)) / divisor


def correlation(table: Table, column_a: str, column_b: str) -> float:
    """Pearson correlation between two numeric columns."""
    a = _numbers(table, column_a)
    b = _numbers(table, column_b)
    if len(a) != len(b):
        raise DataLibError("columns have different numbers of values")
    if len(a) < 2:
        raise DataLibError("need at least two paired values")
    return statistics.correlation(a, b)


def correlation_matrix(
    table: Table, columns: Iterable[str] | None = None
) -> dict[str, dict[str, float]]:
    """Pearson correlation for every pair of numeric columns."""
    cols = list(columns) if columns is not None else numeric_columns(table)
    matrix: dict[str, dict[str, float]] = {}
    for row_name in cols:
        matrix[row_name] = {}
        for col_name in cols:
            if row_name == col_name:
                matrix[row_name][col_name] = 1.0
            else:
                try:
                    matrix[row_name][col_name] = correlation(table, row_name, col_name)
                except DataLibError:
                    matrix[row_name][col_name] = float("nan")
    return matrix


# ----------------------------------------------------------------------
# Describe / group-by
# ----------------------------------------------------------------------
def describe(table: Table, columns: Iterable[str] | None = None) -> dict[str, dict]:
    """Return per-column summary statistics as a mapping of dicts."""
    cols = list(columns) if columns is not None else table.columns
    for name in cols:
        table._require(name)

    summary: dict[str, dict] = {}
    for name in cols:
        values = [v for v in table.column(name) if not is_missing(v)]
        info: dict[str, Any] = {
            "count": len(values),
            "missing": len(table) - len(values),
        }
        if values and all(_is_number(v) for v in values):
            numbers = [float(v) for v in values]
            info.update(
                {
                    "mean": statistics.fmean(numbers),
                    "std": statistics.stdev(numbers) if len(numbers) > 1 else 0.0,
                    "min": min(numbers),
                    "25%": quantile(numbers, 0.25),
                    "50%": quantile(numbers, 0.50),
                    "75%": quantile(numbers, 0.75),
                    "max": max(numbers),
                    "sum": math.fsum(numbers),
                }
            )
        else:
            top = value_counts(table, name)
            info["unique"] = len({str(v) for v in values})
            info["top"] = top[0][0] if top else None
            info["freq"] = top[0][1] if top else 0
        summary[name] = info
    return summary


# Aggregations accepted by :func:`group_by`.
_AGGREGATIONS: dict[str, Callable[[list], Any]] = {
    "count": lambda values: len([v for v in values if not is_missing(v)]),
    "sum": lambda values: math.fsum(v for v in values if _is_number(v)),
    "mean": lambda values: (
        statistics.fmean(v for v in values if _is_number(v))
        if any(_is_number(v) for v in values)
        else None
    ),
    "median": lambda values: statistics.median(
        [v for v in values if _is_number(v)]
    ),
    "min": lambda values: min(v for v in values if not is_missing(v)),
    "max": lambda values: max(v for v in values if not is_missing(v)),
    "std": lambda values: statistics.stdev(
        [v for v in values if _is_number(v)]
    )
    if sum(_is_number(v) for v in values) > 1
    else None,
    "first": lambda values: next((v for v in values if not is_missing(v)), None),
    "last": lambda values: next(
        (v for v in reversed(values) if not is_missing(v)), None
    ),
    "nunique": lambda values: len({str(v) for v in values if not is_missing(v)}),
}


def _apply_aggregation(values: list, agg) -> Any:
    if callable(agg):
        return agg(values)
    if agg not in _AGGREGATIONS:
        raise DataLibError(f"unknown aggregation: {agg!r}")
    return _AGGREGATIONS[agg](values)


def group_by(
    table: Table,
    by: str | Iterable[str],
    aggregations: Mapping[str, tuple[str, Any]],
) -> Table:
    """Group rows and aggregate.

    Parameters
    ----------
    by:
        One or more key columns whose distinct combinations define groups.
    aggregations:
        Mapping of output column name to ``(input_column, aggregation)`` where
        ``aggregation`` is a built-in name (``"count"``, ``"sum"``, ``"mean"``,
        ``"median"``, ``"min"``, ``"max"``, ``"std"``, ``"first"``, ``"last"``,
        ``"nunique"``) or a callable receiving the list of values.

    Returns
    -------
    Table
        One row per group, ordered by the grouping columns.
    """
    keys = [by] if isinstance(by, str) else list(by)
    for name in keys:
        table._require(name)
    for out_name, spec in aggregations.items():
        if not (isinstance(spec, tuple) and len(spec) == 2):
            raise DataLibError(
                f"aggregation for {out_name!r} must be (column, aggregation)"
            )
        table._require(spec[0])

    groups: dict[tuple, list[dict]] = {}
    order: list[tuple] = []
    for row in table.rows:
        key = tuple(row[k] for k in keys)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    out_columns = keys + list(aggregations)
    rows = []
    for key in order:
        group = groups[key]
        record = dict(zip(keys, key))
        for out_name, (source, agg) in aggregations.items():
            record[out_name] = _apply_aggregation(
                [row[source] for row in group], agg
            )
        rows.append(record)
    return Table(out_columns, rows)
