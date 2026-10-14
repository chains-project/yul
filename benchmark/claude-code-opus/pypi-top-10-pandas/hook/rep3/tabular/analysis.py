"""Descriptive statistics and aggregation."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any, Callable, Iterable

from ._util import is_missing as _is_missing, is_numeric as _is_numeric
from .table import Table


def _present(values: Iterable[Any]) -> list[Any]:
    return [v for v in values if not _is_missing(v)]


def numeric_columns(table: Table) -> list[str]:
    """Columns whose non-missing values are all int/float (and at least one exists)."""
    out = []
    for c in table.columns:
        values = _present(table.column(c))
        if values and _is_numeric(values):
            out.append(c)
    return out


def summarize_column(values: Iterable[Any]) -> dict[str, Any]:
    """Summary statistics for one column.

    Always includes count, missing and unique. Numeric columns add mean, std,
    min, 25%, 50%, 75%, max; other columns add top and freq.
    """
    values = list(values)
    present = _present(values)
    summary: dict[str, Any] = {
        "count": len(present),
        "missing": len(values) - len(present),
        "unique": len(set(present)),
    }
    if present and _is_numeric(present):
        if len(present) > 1:
            q1, q2, q3 = statistics.quantiles(present, n=4, method="inclusive")
            std = statistics.stdev(present)
        else:
            q1 = q2 = q3 = present[0]
            std = None
        summary.update(
            mean=statistics.fmean(present),
            std=std,
            min=min(present),
            **{"25%": q1, "50%": q2, "75%": q3},
            max=max(present),
        )
    elif present:
        top, freq = Counter(present).most_common(1)[0]
        summary.update(top=top, freq=freq)
    return summary


def describe(table: Table, columns: Iterable[str] | None = None) -> dict[str, dict[str, Any]]:
    """Map each column name to :func:`summarize_column` output."""
    cols = table.columns if columns is None else list(columns)
    return {c: summarize_column(table.column(c)) for c in cols}


def missing_report(table: Table) -> dict[str, dict[str, float]]:
    """Per-column missing count and fraction."""
    n = len(table)
    report = {}
    for c in table.columns:
        missing = sum(_is_missing(v) for v in table.column(c))
        report[c] = {"missing": missing, "fraction": missing / n if n else 0.0}
    return report


def value_counts(table: Table, column: str, *, dropna: bool = True, normalize: bool = False) -> list[tuple[Any, float]]:
    """(value, count) pairs, most common first. ``normalize`` returns fractions."""
    values = table.column(column)
    if dropna:
        values = _present(values)
    counts = Counter(values).most_common()
    if normalize:
        total = len(values)
        return [(v, c / total) for v, c in counts] if total else []
    return counts


AGGREGATIONS: dict[str, Callable[[list[Any]], Any]] = {
    "count": len,
    "sum": lambda v: sum(v) if v else 0,
    "mean": lambda v: statistics.fmean(v) if v else None,
    "median": lambda v: statistics.median(v) if v else None,
    "min": lambda v: min(v) if v else None,
    "max": lambda v: max(v) if v else None,
    "std": lambda v: statistics.stdev(v) if len(v) > 1 else None,
    "nunique": lambda v: len(set(v)),
    "first": lambda v: v[0] if v else None,
    "last": lambda v: v[-1] if v else None,
}


def group_by(
    table: Table,
    by: str | Iterable[str],
    aggregations: dict[str, str | Callable[[list[Any]], Any] | Iterable[str | Callable[[list[Any]], Any]]],
) -> Table:
    """Group rows and aggregate.

    ``aggregations`` maps a column to an aggregation name (see
    :data:`AGGREGATIONS`), a callable, or a list of those. Missing values are
    excluded before aggregating, so a custom callable may receive an empty
    list. Output columns are named ``<column>_<agg>``;
    groups appear in first-seen order.

    Example::

        group_by(t, "region", {"sales": ["sum", "mean"], "order_id": "count"})
    """
    keys = [by] if isinstance(by, str) else list(by)
    for k in keys:
        if k not in table.columns:
            raise KeyError(k)
    key_idx = [table.columns.index(k) for k in keys]

    specs: list[tuple[str, int, Callable[[list[Any]], Any]]] = []
    for col, aggs in aggregations.items():
        if col not in table.columns:
            raise KeyError(col)
        if isinstance(aggs, str) or callable(aggs):
            aggs = [aggs]
        for agg in aggs:
            if isinstance(agg, str):
                if agg not in AGGREGATIONS:
                    raise ValueError(f"unknown aggregation {agg!r}; choose from {sorted(AGGREGATIONS)}")
                name, fn = agg, AGGREGATIONS[agg]
            else:
                name, fn = getattr(agg, "__name__", "agg"), agg
            specs.append((f"{col}_{name}", table.columns.index(col), fn))

    groups: dict[tuple[Any, ...], list[list[Any]]] = {}
    for row in table.rows:
        groups.setdefault(tuple(row[i] for i in key_idx), []).append(row)

    out_rows = []
    for key, rows in groups.items():
        out_rows.append(list(key) + [fn(_present(r[i] for r in rows)) for _, i, fn in specs])
    return Table(keys + [name for name, _, _ in specs], out_rows)


def correlation(table: Table, x: str, y: str) -> float | None:
    """Pearson correlation of two numeric columns over rows where both are present.

    Returns ``None`` if fewer than two complete pairs or either column is constant.
    """
    pairs = [(a, b) for a, b in zip(table.column(x), table.column(y)) if not _is_missing(a) and not _is_missing(b)]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    if not (_is_numeric(xs) and _is_numeric(ys)):
        raise TypeError(f"columns {x!r} and {y!r} must be numeric")
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return None


def correlation_matrix(table: Table, columns: Iterable[str] | None = None) -> dict[str, dict[str, float | None]]:
    """Pairwise Pearson correlations between numeric columns."""
    cols = numeric_columns(table) if columns is None else list(columns)
    return {a: {b: (1.0 if a == b else correlation(table, a, b)) for b in cols} for a in cols}


def format_describe(stats: dict[str, dict[str, Any]]) -> str:
    """Render :func:`describe` output as a plain-text table (stats as rows)."""
    if not stats:
        return ""
    fields: list[str] = []
    for s in stats.values():
        fields.extend(f for f in s if f not in fields)

    def fmt(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, float):
            return "nan" if math.isnan(v) else f"{v:.4g}"
        return str(v)

    header = [""] + list(stats)
    body = [[f] + [fmt(stats[c].get(f)) for c in stats] for f in fields]
    widths = [max(len(str(r[i])) for r in [header] + body) for i in range(len(header))]
    lines = ["  ".join(str(cell).rjust(w) for cell, w in zip(r, widths)) for r in [header] + body]
    return "\n".join(lines)
