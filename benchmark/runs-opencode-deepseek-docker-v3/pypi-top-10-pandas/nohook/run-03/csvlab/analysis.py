"""Descriptive analysis for :class:`~csvlab.table.Table`."""

from __future__ import annotations

import math
import statistics
from typing import Any, Callable, Iterable, Sequence

from .table import Table


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def numeric_values(values: Iterable[Any]) -> list[float]:
    return [float(v) for v in values if _is_number(v)]


def missing_count(values: Sequence[Any]) -> int:
    return sum(
        v is None or (isinstance(v, str) and v.strip() == "") for v in values
    )


def count(values: Sequence[Any]) -> int:
    return sum(
        1 for v in values if not (v is None or (isinstance(v, str) and v.strip() == ""))
    )


def total(values: Sequence[Any]) -> float:
    numbers = numeric_values(values)
    return math.fsum(numbers) if numbers else 0.0


def mean(values: Sequence[Any]) -> float | None:
    numbers = numeric_values(values)
    return statistics.mean(numbers) if numbers else None


def median(values: Sequence[Any]) -> float | None:
    numbers = numeric_values(values)
    return statistics.median(numbers) if numbers else None


def mode(values: Sequence[Any]) -> Any:
    present = [
        v for v in values if not (v is None or (isinstance(v, str) and v.strip() == ""))
    ]
    return statistics.mode(present) if present else None


def variance(values: Sequence[Any], *, sample: bool = True) -> float | None:
    numbers = numeric_values(values)
    if len(numbers) < 2:
        return 0.0 if numbers else None
    return statistics.variance(numbers) if sample else statistics.pvariance(numbers)


def stdev(values: Sequence[Any], *, sample: bool = True) -> float | None:
    numbers = numeric_values(values)
    if len(numbers) < 2:
        return 0.0 if numbers else None
    return statistics.stdev(numbers) if sample else statistics.pstdev(numbers)


def minimum(values: Sequence[Any]) -> Any:
    present = [
        v for v in values if not (v is None or (isinstance(v, str) and v.strip() == ""))
    ]
    return min(present) if present else None


def maximum(values: Sequence[Any]) -> Any:
    present = [
        v for v in values if not (v is None or (isinstance(v, str) and v.strip() == ""))
    ]
    return max(present) if present else None


def column_stats(values: Sequence[Any]) -> dict[str, Any]:
    present = [
        v for v in values if not (v is None or (isinstance(v, str) and v.strip() == ""))
    ]
    numbers = numeric_values(values)
    stats: dict[str, Any] = {
        "count": len(present),
        "missing": len(values) - len(present),
        "unique": len(set(present)),
        "min": minimum(values),
        "max": maximum(values),
        "mean": statistics.mean(numbers) if numbers else None,
        "median": statistics.median(numbers) if numbers else None,
        "stdev": (
            statistics.stdev(numbers) if len(numbers) >= 2 else (0.0 if numbers else None)
        ),
        "sum": math.fsum(numbers) if numbers else None,
    }
    return stats


def describe(
    table: Table,
    columns: Iterable[str] | None = None,
    *,
    numeric_only: bool = True,
) -> dict[str, dict[str, Any]]:
    """Return per-column summary statistics."""

    names = list(columns) if columns is not None else list(table.columns)
    out: dict[str, dict[str, Any]] = {}
    for name in names:
        values = table.column(name)
        if numeric_only and not numeric_values(values):
            continue
        out[name] = column_stats(values)
    return out


def value_counts(
    table: Table,
    column: str,
    *,
    normalize: bool = False,
    sort: bool = True,
    dropna: bool = True,
) -> list[tuple[Any, float]]:
    """Return ``(value, count)`` pairs ordered by descending frequency."""

    counts: dict[Any, int] = {}
    for value in table.column(column):
        if value is None and dropna:
            continue
        counts[value] = counts.get(value, 0) + 1
    items = list(counts.items())
    if sort:
        items.sort(key=lambda item: item[1], reverse=True)
    if normalize:
        denominator = sum(counts.values())
        if denominator == 0:
            return [(value, 0.0) for value, _ in items]
        return [(value, n / denominator) for value, n in items]
    return items


def missing_counts(table: Table) -> dict[str, int]:
    return {name: missing_count(table.column(name)) for name in table.columns}


def covariance(a: Sequence[Any], b: Sequence[Any], *, sample: bool = True) -> float | None:
    pairs = [
        (float(x), float(y))
        for x, y in zip(a, b)
        if _is_number(x) and _is_number(y)
    ]
    n = len(pairs)
    if n < 2:
        return None
    mean_x = math.fsum(x for x, _ in pairs) / n
    mean_y = math.fsum(y for _, y in pairs) / n
    total = math.fsum((x - mean_x) * (y - mean_y) for x, y in pairs)
    return total / (n - 1 if sample else n)


def correlation(table: Table, column_a: str, column_b: str) -> float | None:
    """Pearson correlation coefficient between two columns."""

    a = table.column(column_a)
    b = table.column(column_b)
    pairs = [
        (float(x), float(y))
        for x, y in zip(a, b)
        if _is_number(x) and _is_number(y)
    ]
    n = len(pairs)
    if n < 2:
        return None
    mean_x = math.fsum(x for x, _ in pairs) / n
    mean_y = math.fsum(y for _, y in pairs) / n
    numerator = math.fsum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denom_x = math.sqrt(math.fsum((x - mean_x) ** 2 for x, _ in pairs))
    denom_y = math.sqrt(math.fsum((y - mean_y) ** 2 for _, y in pairs))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def group_by(
    table: Table,
    by: str | Sequence[str],
    aggregations: dict[str, Any],
) -> Table:
    """Aggregate rows by one or more key columns.

    ``aggregations`` maps an output column name to either a callable receiving
    the list of group records, or a ``(source_column, callable)`` pair applied
    to that column's values.
    """

    keys = [by] if isinstance(by, str) else list(by)
    for key in keys:
        table.index(key)
    key_positions = [table.index(k) for k in keys]

    groups: dict[tuple, list[dict[str, Any]]] = {}
    for record in table:
        group_key = tuple(record[k] for k in keys)
        groups.setdefault(group_key, []).append(record)

    out_rows: list[list[Any]] = []
    for group_key, records in groups.items():
        row: list[Any] = list(group_key)
        for output_name, spec in aggregations.items():
            if isinstance(spec, tuple):
                source, func = spec
                values = [record[source] for record in records]
                row.append(func(values))
            else:
                row.append(spec(records))
        out_rows.append(row)

    columns = list(keys) + list(aggregations.keys())
    return Table(columns, out_rows)
