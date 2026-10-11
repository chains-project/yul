"""Statistical analysis and aggregation helpers."""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

from .table import Table

Number = Union[int, float]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def numeric_values(values: Sequence[Any]) -> List[Number]:
    """Return only the numeric (non-boolean, non-missing) values."""
    return [value for value in values if _is_number(value)]


def mean(values: Sequence[Any]) -> Optional[float]:
    """Arithmetic mean, or ``None`` when there are no numeric values."""
    numbers = numeric_values(values)
    return sum(numbers) / len(numbers) if numbers else None


def median(values: Sequence[Any]) -> Optional[float]:
    """Median, or ``None`` when there are no numeric values."""
    numbers = sorted(numeric_values(values))
    n = len(numbers)
    if not n:
        return None
    mid = n // 2
    if n % 2:
        return float(numbers[mid])
    return (numbers[mid - 1] + numbers[mid]) / 2


def variance(values: Sequence[Any]) -> Optional[float]:
    """Sample variance (``n - 1`` denominator), or ``None`` for fewer than 2."""
    numbers = numeric_values(values)
    n = len(numbers)
    if n < 2:
        return None
    avg = sum(numbers) / n
    return sum((value - avg) ** 2 for value in numbers) / (n - 1)


def stdev(values: Sequence[Any]) -> Optional[float]:
    """Sample standard deviation, or ``None`` for fewer than 2 values."""
    var = variance(values)
    return math.sqrt(var) if var is not None else None


def minimum(values: Sequence[Any]) -> Any:
    present = [value for value in values if value is not None]
    try:
        return min(present) if present else None
    except TypeError:
        return None


def maximum(values: Sequence[Any]) -> Any:
    present = [value for value in values if value is not None]
    try:
        return max(present) if present else None
    except TypeError:
        return None


def total(values: Sequence[Any]) -> Optional[float]:
    numbers = numeric_values(values)
    return sum(numbers) if numbers else None


def quantile(values: Sequence[Any], q: float) -> Optional[float]:
    """Linear-interpolation quantile (``q`` in ``[0, 1]``)."""
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be between 0 and 1")
    numbers = sorted(numeric_values(values))
    if not numbers:
        return None
    if len(numbers) == 1:
        return float(numbers[0])
    position = q * (len(numbers) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(numbers[int(position)])
    fraction = position - lower
    return numbers[lower] * (1 - fraction) + numbers[upper] * fraction


def value_counts(
    table: Table,
    column: str,
    normalize: bool = False,
    dropna: bool = True,
) -> Dict[Any, float]:
    """Count occurrences of each value in ``column``, most frequent first."""
    values = table.column(column)
    counts: Dict[Any, int] = {}
    for value in values:
        if value is None and dropna:
            continue
        counts[value] = counts.get(value, 0) + 1
    ordered = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    if normalize:
        denom = sum(ordered.values())
        return {key: count / denom for key, count in ordered.items()} if denom else {}
    return ordered


def correlation(table: Table, column_x: str, column_y: str) -> Optional[float]:
    """Pearson correlation between two numeric columns.

    Returns ``None`` when fewer than two complete pairs exist or either column
    has zero variance.
    """
    xs = table.column(column_x)
    ys = table.column(column_y)
    pairs = [
        (x, y)
        for x, y in zip(xs, ys)
        if _is_number(x) and _is_number(y)
    ]
    n = len(pairs)
    if n < 2:
        return None
    mean_x = sum(pair[0] for pair in pairs) / n
    mean_y = sum(pair[1] for pair in pairs) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    var_x = sum((x - mean_x) ** 2 for x, _ in pairs)
    var_y = sum((y - mean_y) ** 2 for _, y in pairs)
    if var_x == 0 or var_y == 0:
        return None
    return cov / math.sqrt(var_x * var_y)


def _mode(values: Sequence[Any]) -> Any:
    counts: Dict[Any, int] = {}
    for value in values:
        if value is None:
            continue
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return None
    return max(counts, key=counts.get)


def _first(values: Sequence[Any]) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _last(values: Sequence[Any]) -> Any:
    for value in reversed(values):
        if value is not None:
            return value
    return None


def _nunique(values: Sequence[Any]) -> int:
    return len({value for value in values if value is not None})


_AGGREGATORS: Dict[str, Callable[[Sequence[Any]], Any]] = {
    "count": lambda values: sum(1 for value in values if value is not None),
    "size": len,
    "sum": total,
    "mean": mean,
    "median": median,
    "stdev": stdev,
    "variance": variance,
    "min": minimum,
    "max": maximum,
    "mode": _mode,
    "first": _first,
    "last": _last,
    "nunique": _nunique,
}


def _resolve_aggregator(spec: Union[str, Callable[[Sequence[Any]], Any]]):
    if callable(spec):
        return spec, getattr(spec, "__name__", "agg")
    if spec not in _AGGREGATORS:
        raise ValueError(
            f"unknown aggregation {spec!r}; expected one of {sorted(_AGGREGATORS)!r}"
        )
    return _AGGREGATORS[spec], spec


def summary(table: Table, columns: Optional[Sequence[str]] = None) -> Dict[str, Dict[str, Any]]:
    """Return per-column summary statistics as ``{column: {stat: value}}``."""
    targets = table.columns if columns is None else list(columns)
    result: Dict[str, Dict[str, Any]] = {}
    for name in targets:
        values = table.column(name)
        present = [value for value in values if value is not None]
        result[name] = {
            "count": len(present),
            "missing": len(values) - len(present),
            "unique": _nunique(values),
            "mean": mean(values),
            "median": median(values),
            "stdev": stdev(values),
            "min": minimum(values),
            "max": maximum(values),
            "mode": _mode(values),
        }
    return result


_STAT_COLUMNS = [
    "column",
    "count",
    "missing",
    "unique",
    "mean",
    "median",
    "stdev",
    "min",
    "max",
    "mode",
]


def describe(table: Table, columns: Optional[Sequence[str]] = None) -> Table:
    """Return a table of summary statistics, one row per column."""
    stats = summary(table, columns)
    rows = []
    for name, values in stats.items():
        row = {"column": name}
        row.update(values)
        rows.append(row)
    return Table.from_dicts(rows, columns=_STAT_COLUMNS)


def group_by(
    table: Table,
    by: Union[str, Sequence[str]],
    aggregations: Optional[Mapping[str, Union[str, Callable, Sequence]]] = None,
) -> Table:
    """Group rows by one or more columns and aggregate.

    ``aggregations`` maps a source column to an aggregation name, a callable,
    or a sequence of either (for example ``{"sales": ["mean", "max"]}``). When
    omitted, only a ``count`` of rows per group is produced.
    """
    by_columns = [by] if isinstance(by, str) else list(by)
    if not by_columns:
        raise ValueError("at least one grouping column is required")
    for name in by_columns:
        if name not in table:
            raise KeyError(f"unknown column: {name!r}")

    plan: List[tuple] = []
    if aggregations is None:
        plan.append((by_columns[0], _AGGREGATORS["count"], "count"))
    else:
        for source, spec in aggregations.items():
            if source not in table:
                raise KeyError(f"unknown column: {source!r}")
            specs = [spec] if isinstance(spec, str) or callable(spec) else list(spec)
            for item in specs:
                func, label = _resolve_aggregator(item)
                plan.append((source, func, f"{source}_{label}"))

    groups: Dict[tuple, List[Mapping[str, Any]]] = {}
    order: List[tuple] = []
    for row in table.rows(named=True):
        key = tuple(row[name] for name in by_columns)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    rows = []
    for key in order:
        members = groups[key]
        row: Dict[str, Any] = dict(zip(by_columns, key))
        for source, func, output in plan:
            row[output] = func([member[source] for member in members])
        rows.append(row)

    output_columns = list(by_columns) + [item[2] for item in plan]
    return Table.from_dicts(rows, columns=output_columns)
