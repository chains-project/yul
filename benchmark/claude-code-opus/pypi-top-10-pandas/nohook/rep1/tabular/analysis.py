"""Descriptive statistics, frequency counts, correlation, and grouped aggregation."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any, Callable, Mapping, Sequence

from .clean import _is_missing, _is_number
from .table import Table


def _quantile(sorted_values: Sequence[float], q: float) -> float:
    """Linear-interpolated quantile (same method as numpy's default)."""
    pos = (len(sorted_values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def describe(table: Table, columns: Sequence[str] | None = None) -> dict[str, dict[str, Any]]:
    """Summary statistics per column.

    Numeric columns get count/missing/mean/std/min/25%/50%/75%/max.
    Other columns get count/missing/unique/top/freq.
    """
    result = {}
    for col in columns or table.columns:
        values = table[col]
        present = [v for v in values if not _is_missing(v)]
        stats: dict[str, Any] = {"count": len(present), "missing": len(values) - len(present)}
        if present and all(_is_number(v) for v in present):
            ordered = sorted(present)
            stats.update(
                mean=statistics.fmean(ordered),
                std=statistics.stdev(ordered) if len(ordered) > 1 else None,
                min=ordered[0],
                **{"25%": _quantile(ordered, 0.25), "50%": _quantile(ordered, 0.5),
                   "75%": _quantile(ordered, 0.75)},
                max=ordered[-1],
            )
        else:
            counts = Counter(present)
            top = counts.most_common(1)
            stats.update(
                unique=len(counts),
                top=top[0][0] if top else None,
                freq=top[0][1] if top else 0,
            )
        result[col] = stats
    return result


def value_counts(table: Table, column: str, dropna: bool = True) -> list[tuple[Any, int]]:
    """Frequency of each distinct value, most common first."""
    values = table[column]
    if dropna:
        values = [v for v in values if not _is_missing(v)]
    return Counter(values).most_common()


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    pairs = [(x, y) for x, y in zip(xs, ys) if not _is_missing(x) and not _is_missing(y)]
    if len(pairs) < 2:
        return None
    px, py = zip(*pairs)
    try:
        return statistics.correlation(px, py)
    except statistics.StatisticsError:  # constant input
        return None


def correlation(table: Table, columns: Sequence[str] | None = None) -> dict[str, dict[str, float | None]]:
    """Pairwise Pearson correlation between numeric columns.

    Rows where either value is missing are excluded per pair. Pairs with fewer
    than two complete rows or zero variance yield ``None``.
    """
    if columns is None:
        columns = [
            c for c in table.columns
            if (present := [v for v in table[c] if not _is_missing(v)])
            and all(_is_number(v) for v in present)
        ]
    data = {c: table[c] for c in columns}
    return {a: {b: (1.0 if a == b else _pearson(data[a], data[b])) for b in columns} for a in columns}


def _numeric(values: list[Any]) -> list[float]:
    return [v for v in values if _is_number(v)]


AGGREGATIONS: dict[str, Callable[[list[Any]], Any]] = {
    "count": lambda vs: sum(1 for v in vs if not _is_missing(v)),
    "size": len,
    "sum": lambda vs: sum(_numeric(vs)),
    "mean": lambda vs: statistics.fmean(n) if (n := _numeric(vs)) else None,
    "median": lambda vs: statistics.median(n) if (n := _numeric(vs)) else None,
    "min": lambda vs: min(p) if (p := [v for v in vs if not _is_missing(v)]) else None,
    "max": lambda vs: max(p) if (p := [v for v in vs if not _is_missing(v)]) else None,
    "std": lambda vs: statistics.stdev(n) if len(n := _numeric(vs)) > 1 else None,
    "nunique": lambda vs: len({v for v in vs if not _is_missing(v)}),
    "first": lambda vs: vs[0] if vs else None,
}


def group_by(
    table: Table,
    keys: str | Sequence[str],
    aggregations: Mapping[str, str | Callable[[list[Any]], Any] | Sequence[str | Callable]],
) -> Table:
    """Group rows by key column(s) and aggregate other columns.

    ``aggregations`` maps a column name to an aggregation name from
    :data:`AGGREGATIONS`, a callable taking the list of group values, or a list
    of either. Output columns are named ``<column>_<agg>``. Groups appear in
    order of first occurrence.

        >>> group_by(t, "region", {"sales": ["sum", "mean"], "id": "count"})
    """
    keys = [keys] if isinstance(keys, str) else list(keys)
    groups: dict[tuple, list[int]] = {}
    for i, row in enumerate(table.rows()):
        groups.setdefault(tuple(row[k] for k in keys), []).append(i)

    specs = []
    for col, aggs in aggregations.items():
        if isinstance(aggs, str) or callable(aggs):
            aggs = [aggs]
        for agg in aggs:
            if isinstance(agg, str):
                if agg not in AGGREGATIONS:
                    raise ValueError(f"unknown aggregation {agg!r}; choose from {sorted(AGGREGATIONS)}")
                specs.append((col, f"{col}_{agg}", AGGREGATIONS[agg]))
            else:
                specs.append((col, f"{col}_{getattr(agg, '__name__', 'agg')}", agg))

    out: dict[str, list[Any]] = {k: [] for k in keys}
    out.update({name: [] for _, name, _ in specs})
    source = {col: table[col] for col, _, _ in specs}
    for key, idx in groups.items():
        for k, v in zip(keys, key):
            out[k].append(v)
        for col, name, fn in specs:
            out[name].append(fn([source[col][i] for i in idx]))
    return Table(out)
