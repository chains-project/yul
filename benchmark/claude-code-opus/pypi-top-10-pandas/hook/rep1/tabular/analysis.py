"""Descriptive statistics, grouping and correlation."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any, Callable, Iterable, Mapping, Sequence

from .table import Table

Aggregator = str | Callable[[list[Any]], Any]


def is_numeric(values: Iterable[Any]) -> bool:
    """True if every non-missing value is an int/float (bools excluded)."""
    present = [v for v in values if v is not None]
    return bool(present) and all(
        isinstance(v, (int, float)) and not isinstance(v, bool) for v in present)


def numeric_columns(table: Table) -> list[str]:
    return [c for c in table.columns if is_numeric(table[c])]


def column_types(table: Table) -> dict[str, str]:
    """Map each column to the name of its (single) value type, or ``"mixed"``."""
    result = {}
    for name in table.columns:
        kinds = {type(v).__name__ for v in table[name] if v is not None}
        if kinds == {"int", "float"}:
            kinds = {"float"}
        result[name] = kinds.pop() if len(kinds) == 1 else ("empty" if not kinds else "mixed")
    return result


def missing_report(table: Table) -> Table:
    """Count and percentage of missing values per column."""
    n = len(table)
    counts = [table[c].count(None) for c in table.columns]
    return Table({
        "column": table.columns,
        "missing": counts,
        "percent": [round(100 * c / n, 2) if n else 0.0 for c in counts],
    })


def describe(table: Table, columns: Sequence[str] | None = None) -> dict[str, dict[str, Any]]:
    """Summary statistics per column.

    Numeric columns get count/missing/mean/std/min/25%/50%/75%/max.
    Other columns get count/missing/unique/top/freq.
    """
    summary: dict[str, dict[str, Any]] = {}
    for name in columns if columns is not None else table.columns:
        values = table[name]
        present = [v for v in values if v is not None]
        stats: dict[str, Any] = {"count": len(present), "missing": len(values) - len(present)}
        if is_numeric(values):
            stats.update(
                mean=statistics.fmean(present),
                std=statistics.stdev(present) if len(present) > 1 else None,
                min=min(present),
                **dict(zip(("25%", "50%", "75%"), _quartiles(present))),
                max=max(present),
            )
        else:
            counts = Counter(present)
            top = counts.most_common(1)
            stats.update(unique=len(counts),
                         top=top[0][0] if top else None,
                         freq=top[0][1] if top else 0)
        summary[name] = stats
    return summary


def value_counts(table: Table, column: str, normalize: bool = False,
                 dropna: bool = True) -> list[tuple[Any, int | float]]:
    """Frequency of each distinct value, most common first."""
    values = table[column]
    if dropna:
        values = [v for v in values if v is not None]
    counts = Counter(values).most_common()
    if normalize and values:
        return [(v, c / len(values)) for v, c in counts]
    return counts


def _first(values: list[Any]) -> Any:
    return values[0] if values else None


def _last(values: list[Any]) -> Any:
    return values[-1] if values else None


def _or_none(func: Callable[[list[Any]], Any], minimum: int = 1) -> Callable[[list[Any]], Any]:
    return lambda values: func(values) if len(values) >= minimum else None


AGGREGATORS: dict[str, Callable[[list[Any]], Any]] = {
    "count": len,
    "sum": lambda values: sum(values),
    "mean": _or_none(statistics.fmean),
    "median": _or_none(statistics.median),
    "min": _or_none(min),
    "max": _or_none(max),
    "std": _or_none(statistics.stdev, 2),
    "var": _or_none(statistics.variance, 2),
    "nunique": lambda values: len(set(values)),
    "first": _first,
    "last": _last,
}


def group_by(table: Table, by: str | Sequence[str],
             aggregations: Mapping[str, Aggregator | Sequence[Aggregator]]) -> Table:
    """Group rows and aggregate.

    ``aggregations`` maps a column to an aggregator name (see
    :data:`AGGREGATORS`), a callable, or a list of them. Missing values are
    excluded before aggregating. Output columns are named ``<column>_<agg>``.
    Groups appear in order of first occurrence; rows with a missing key are
    grouped under ``None``.

    Example::

        group_by(sales, "region", {"revenue": ["sum", "mean"], "order_id": "count"})
    """
    keys = [by] if isinstance(by, str) else list(by)
    groups: dict[tuple, list[int]] = {}
    key_columns = [table[k] for k in keys]
    for i in range(len(table)):
        groups.setdefault(tuple(col[i] for col in key_columns), []).append(i)

    output: dict[str, list[Any]] = {k: [g[j] for g in groups] for j, k in enumerate(keys)}
    for column, aggs in aggregations.items():
        values = table[column]
        for agg in [aggs] if isinstance(aggs, str) or callable(aggs) else aggs:
            func = AGGREGATORS[agg] if isinstance(agg, str) else agg
            label = agg if isinstance(agg, str) else getattr(agg, "__name__", "agg")
            output[f"{column}_{label}"] = [
                func([values[i] for i in idx if values[i] is not None])
                for idx in groups.values()
            ]
    return Table(output)


def correlation(table: Table, x: str, y: str) -> float | None:
    """Pearson correlation of two numeric columns over rows where both are present.

    Returns ``None`` if fewer than two complete pairs exist or either column
    is constant.
    """
    pairs = [(a, b) for a, b in zip(table[x], table[y]) if a is not None and b is not None]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return None


def correlation_matrix(table: Table, columns: Sequence[str] | None = None) -> dict[str, dict[str, float | None]]:
    """Pairwise Pearson correlations between numeric columns."""
    names = list(columns) if columns is not None else numeric_columns(table)
    return {a: {b: 1.0 if a == b else correlation(table, a, b) for b in names} for a in names}


def histogram(table: Table, column: str, bins: int = 10) -> list[tuple[float, float, int]]:
    """Equal-width histogram as ``(lower, upper, count)`` triples.

    Each bin is half-open ``[lower, upper)`` except the last, which also
    includes the maximum.
    """
    values = [v for v in table[column] if v is not None]
    if not values:
        return []
    low, high = min(values), max(values)
    if low == high:
        return [(low, high, len(values))]
    width = (high - low) / bins
    counts = [0] * bins
    for v in values:
        counts[min(int((v - low) / width), bins - 1)] += 1
    return [(low + i * width, low + (i + 1) * width, c) for i, c in enumerate(counts)]


def _quartiles(values: list[float]) -> list[float]:
    if len(values) == 1:
        return [values[0]] * 3
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return [q1, q2, q3]


def format_describe(summary: Mapping[str, Mapping[str, Any]]) -> str:
    """Render the output of :func:`describe` as a plain-text table."""
    stats: list[str] = []
    for col in summary.values():
        stats.extend(s for s in col if s not in stats)
    rows = [["", *summary]]
    for stat in stats:
        rows.append([stat, *(_fmt(summary[c].get(stat, "")) for c in summary)])
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(cell.rjust(w) for cell, w in zip(r, widths)) for r in rows)


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return "nan" if math.isnan(value) else f"{value:.4g}"
    return str(value)
