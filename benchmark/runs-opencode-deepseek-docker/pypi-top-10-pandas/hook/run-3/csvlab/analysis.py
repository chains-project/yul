"""Analysis helpers for :class:`csvlab.table.Table`."""

from __future__ import annotations

from statistics import mean as _mean, median as _median, pstdev, stdev as _stdev
from typing import Any, Callable, Iterable, Mapping, Sequence

from ._common import is_number


def _new(table: Any, columns: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> Any:
    return table.__class__(columns, rows)


def _numeric_values(table: Any, column: str) -> list[Any]:
    if column not in table.columns:
        raise KeyError(column)
    return [v for v in table[column] if is_number(v)]


def _require_numeric(table: Any, column: str) -> list[Any]:
    values = _numeric_values(table, column)
    if not values:
        raise TypeError(f"column {column!r} has no numeric values")
    return values


def _quantile(sorted_values: Sequence[float], q: float) -> float:
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def describe(table: Any) -> dict[str, dict[str, Any]]:
    """Return per-column summary statistics.

    Numeric columns report count/missing/mean/std/quartiles; other columns
    report count/missing/unique/most-common value and its frequency.
    """
    summary: dict[str, dict[str, Any]] = {}
    for col in table.columns:
        values = table[col]
        present = [v for v in values if v is not None]
        missing = len(values) - len(present)
        numeric = present and all(is_number(v) for v in present)

        if numeric:
            ordered = sorted(present)
            summary[col] = {
                "count": len(present),
                "missing": missing,
                "mean": _mean(present),
                "std": pstdev(present) if len(present) > 1 else 0.0,
                "min": ordered[0],
                "q1": _quantile(ordered, 0.25),
                "median": _median(present),
                "q3": _quantile(ordered, 0.75),
                "max": ordered[-1],
                "sum": sum(present),
            }
        else:
            counts: dict[Any, int] = {}
            for value in present:
                counts[value] = counts.get(value, 0) + 1
            top_value, top_count = (None, 0)
            if counts:
                top_value = max(counts, key=counts.get)
                top_count = counts[top_value]
            summary[col] = {
                "count": len(present),
                "missing": missing,
                "unique": len(counts),
                "top": top_value,
                "freq": top_count,
            }
    return summary


def value_counts(
    table: Any,
    column: str,
    *,
    top: int | None = None,
) -> list[tuple[Any, int]]:
    """Return ``(value, count)`` pairs sorted by descending frequency."""
    if column not in table.columns:
        raise KeyError(column)
    counts: dict[Any, int] = {}
    for value in table[column]:
        if value is not None:
            counts[value] = counts.get(value, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    if top is not None:
        ordered = ordered[:top]
    return ordered


def mean(table: Any, column: str) -> float:
    return _mean(_require_numeric(table, column))


def median(table: Any, column: str) -> float:
    return _median(_require_numeric(table, column))


def stdev(table: Any, column: str) -> float:
    values = _require_numeric(table, column)
    return _stdev(values) if len(values) > 1 else 0.0


def correlation(table: Any, column_a: str, column_b: str) -> float:
    """Pearson correlation over rows where both columns are numeric."""
    pairs = [
        (row.get(column_a), row.get(column_b))
        for row in table.rows
        if is_number(row.get(column_a)) and is_number(row.get(column_b))
    ]
    if len(pairs) < 2:
        raise ValueError("correlation requires at least two paired numeric values")
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mean_x, mean_y = _mean(xs), _mean(ys)
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x == 0 or var_y == 0:
        return 0.0
    return covariance / (var_x**0.5 * var_y**0.5)


def group_by(table: Any, keys: Sequence[str]) -> dict[tuple, Any]:
    """Group rows by one or more columns, returning keyed sub-tables."""
    keys = list(keys)
    unknown = [k for k in keys if k not in table.columns]
    if unknown:
        raise KeyError(f"unknown columns: {unknown}")
    groups: dict[tuple, list[dict[str, Any]]] = {}
    for row in table.rows:
        group_key = tuple(row.get(k) for k in keys)
        groups.setdefault(group_key, []).append(row)
    return {key: _new(table, table.columns, rows) for key, rows in groups.items()}


def _count(values: list[Any]) -> int:
    return len(values)


def _sum(values: list[Any]) -> Any:
    return sum(values) if values else None


def _min(values: list[Any]) -> Any:
    return min(values) if values else None


def _max(values: list[Any]) -> Any:
    return max(values) if values else None


def _first(values: list[Any]) -> Any:
    return values[0] if values else None


def _last(values: list[Any]) -> Any:
    return values[-1] if values else None


def _nunique(values: list[Any]) -> int:
    return len(set(values))


def _mode(values: list[Any]) -> Any:
    if not values:
        return None
    counts: dict[Any, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return max(counts, key=counts.get)


_AGGREGATORS: dict[str, Callable[[list[Any]], Any]] = {
    "count": _count,
    "sum": _sum,
    "mean": lambda values: _mean(values) if values else None,
    "median": lambda values: _median(values) if values else None,
    "min": _min,
    "max": _max,
    "stdev": lambda values: _stdev(values) if len(values) > 1 else (0.0 if values else None),
    "first": _first,
    "last": _last,
    "nunique": _nunique,
    "mode": _mode,
}


def aggregate(
    table: Any,
    by: Sequence[str],
    aggregations: Mapping[str, str | Callable[[list[Any]], Any]],
) -> Any:
    """Group by ``by`` and apply aggregations, returning a new table.

    ``aggregations`` maps a source column to either a preset name (``count``,
    ``sum``, ``mean``, ``median``, ``min``, ``max``, ``stdev``, ``first``,
    ``last``, ``nunique``, ``mode``) or a callable receiving the non-missing
    values for that group.
    """
    by = list(by)
    unknown = [k for k in by if k not in table.columns]
    if unknown:
        raise KeyError(f"unknown columns: {unknown}")

    output_columns = list(by)
    for column, spec in aggregations.items():
        if column not in table.columns:
            raise KeyError(column)
        label = spec if isinstance(spec, str) else getattr(spec, "__name__", "agg")
        output_columns.append(f"{column}_{label}")

    groups: dict[tuple, list[dict[str, Any]]] = {}
    for row in table.rows:
        group_key = tuple(row.get(k) for k in by)
        groups.setdefault(group_key, []).append(row)

    output_rows = []
    for group_key, group_rows in groups.items():
        result = {key: value for key, value in zip(by, group_key)}
        for column, spec in aggregations.items():
            values = [row.get(column) for row in group_rows if row.get(column) is not None]
            if callable(spec):
                result[f"{column}_{getattr(spec, '__name__', 'agg')}"] = spec(values)
            else:
                aggregator = _AGGREGATORS.get(spec)
                if aggregator is None:
                    raise ValueError(f"unknown aggregation: {spec!r}")
                result[f"{column}_{spec}"] = aggregator(values)
        output_rows.append(result)

    return _new(table, output_columns, output_rows)
