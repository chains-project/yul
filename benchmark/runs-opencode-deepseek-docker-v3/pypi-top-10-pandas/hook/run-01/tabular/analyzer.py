"""Descriptive statistics and aggregation for :class:`~tabular.table.Table`."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .table import Table

Numeric = (int, float)


def _numeric(values: Sequence[Any]) -> list[float]:
    return [
        float(v)
        for v in values
        if isinstance(v, Numeric) and not isinstance(v, bool)
    ]


@dataclass
class ColumnStats:
    """Summary statistics for a single column."""

    name: str
    dtype: str
    count: int
    missing: int
    unique: int
    min: Any = None
    max: Any = None
    mean: float | None = None
    median: float | None = None
    stdev: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def column_type(values: Sequence[Any]) -> str:
    """Return a coarse type label for a sequence of cells.

    One of ``"empty"``, ``"int"``, ``"float"``, ``"bool"`` or ``"str"``.
    """
    present = [v for v in values if v is not None]
    if not present:
        return "empty"
    if all(isinstance(v, bool) for v in present):
        return "bool"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in present):
        return "int"
    if all(isinstance(v, Numeric) and not isinstance(v, bool) for v in present):
        return "float"
    return "str"


def column_types(table: Table) -> dict[str, str]:
    """Map each column name to its inferred type label."""
    return {name: column_type(table.column(name)) for name in table.columns}


def _median(values: list[float]) -> float | None:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        return None
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _stdev(values: list[float]) -> float | None:
    n = len(values)
    if n < 2:
        return 0.0 if n == 1 else None
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(variance)


def describe(table: Table) -> dict[str, ColumnStats]:
    """Return :class:`ColumnStats` keyed by column name for every column."""
    report: dict[str, ColumnStats] = {}
    for name in table.columns:
        values = table.column(name)
        present = [v for v in values if v is not None]
        numbers = _numeric(present)
        non_numeric = [v for v in present if not isinstance(v, Numeric)]
        report[name] = ColumnStats(
            name=name,
            dtype=column_type(values),
            count=len(present),
            missing=len(values) - len(present),
            unique=len(set(present)),
            min=min(non_numeric or numbers, default=None),
            max=max(non_numeric or numbers, default=None),
            mean=sum(numbers) / len(numbers) if numbers else None,
            median=_median(numbers),
            stdev=_stdev(numbers),
        )
    return report


def value_counts(
    table: Table, column: str, *, top: int | None = None
) -> dict[Any, int]:
    """Count occurrences of each value in ``column``, most common first."""
    counts = Counter(table.column(column))
    items = counts.most_common(top)
    return dict(items)


def correlation(table: Table, x: str, y: str) -> float | None:
    """Pearson correlation between two numeric columns.

    Returns ``None`` when fewer than two paired values exist or either column
    has zero variance.
    """
    pairs = [
        (a, b)
        for a, b in zip(table.column(x), table.column(y))
        if isinstance(a, Numeric)
        and isinstance(b, Numeric)
        and not isinstance(a, bool)
        and not isinstance(b, bool)
    ]
    if len(pairs) < 2:
        return None
    xs = [float(a) for a, _ in pairs]
    ys = [float(b) for _, b in pairs]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    var_x = sum((a - mx) ** 2 for a in xs)
    var_y = sum((b - my) ** 2 for b in ys)
    if var_x == 0 or var_y == 0:
        return None
    return cov / math.sqrt(var_x * var_y)


def group_by(table: Table, key: str) -> dict[Any, Table]:
    """Partition rows by the value of ``key``, returning ``{value: Table}``."""
    index = table._index(key)
    buckets: dict[Any, list[list[Any]]] = {}
    for row in table.rows:
        buckets.setdefault(row[index], []).append(list(row))
    return {value: Table(table.columns, rows) for value, rows in buckets.items()}


def aggregate(
    table: Table,
    key: str,
    aggregations: Mapping[str, tuple[str, Callable[[Sequence[Any]], Any]]],
) -> Table:
    """Group by ``key`` and compute aggregates.

    ``aggregations`` maps an output column name to a ``(source_column, func)``
    pair, where ``func`` receives the list of values for that group.
    """
    groups = group_by(table, key)
    columns = [key] + list(aggregations)
    rows: list[list[Any]] = []
    for value, group in groups.items():
        row: list[Any] = [value]
        for source, func in aggregations.values():
            row.append(func(group.column(source)))
        rows.append(row)
    return Table(columns, rows)
