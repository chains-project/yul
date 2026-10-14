"""Descriptive statistics and aggregation."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any, Callable, Mapping, Sequence

from .clean import _hashable, _is_number
from .table import Table

Aggregator = Callable[[list[Any]], Any]


def _std(values: list[Any]) -> float | None:
    return statistics.stdev(values) if len(values) > 1 else None


AGGREGATIONS: dict[str, Aggregator] = {
    "count": len,
    "sum": lambda vs: sum(vs) if vs else 0,
    "mean": lambda vs: statistics.fmean(vs) if vs else None,
    "median": lambda vs: statistics.median(vs) if vs else None,
    "min": lambda vs: min(vs) if vs else None,
    "max": lambda vs: max(vs) if vs else None,
    "std": _std,
    "nunique": lambda vs: len({_hashable(v) for v in vs}),
}


def is_numeric(values: Sequence[Any]) -> bool:
    """True if every non-missing value is an int or float (bools excluded)."""
    present = [v for v in values if v is not None]
    return bool(present) and all(_is_number(v) for v in present)


def describe(table: Table, columns: Sequence[str] | None = None) -> Table:
    """Summary statistics, one row per column.

    Every column gets ``count`` (non-missing), ``missing`` and ``unique``.
    Numeric columns also get mean, std, min, 25%, 50%, 75% and max;
    non-numeric columns get ``top`` (most frequent value) and ``freq``.
    """
    cols = list(columns) if columns is not None else table.columns
    out = []
    for col in cols:
        values = table.column(col)
        present = [v for v in values if v is not None]
        stats: dict[str, Any] = {
            "column": col,
            "count": len(present),
            "missing": len(values) - len(present),
            "unique": len({_hashable(v) for v in present}),
        }
        if is_numeric(present):
            q1, q2, q3 = _quartiles(present)
            stats.update(
                mean=statistics.fmean(present),
                std=_std(present),
                min=min(present),
                **{"25%": q1, "50%": q2, "75%": q3},
                max=max(present),
            )
        elif present:
            top, freq = Counter(_hashable(v) for v in present).most_common(1)[0]
            stats.update(top=top, freq=freq)
        out.append(stats)
    header = ["column", "count", "missing", "unique", "mean", "std", "min", "25%", "50%", "75%", "max", "top", "freq"]
    used = [h for h in header if any(h in s for s in out)]
    return Table(used, out)


def value_counts(table: Table, column: str, *, dropna: bool = True, normalize: bool = False) -> Table:
    """Frequency of each distinct value in ``column``, most common first."""
    values = table.column(column)
    if dropna:
        values = [v for v in values if v is not None]
    counts = Counter(_hashable(v) for v in values).most_common()
    total = len(values)
    key = "proportion" if normalize else "count"
    return Table(
        [column, key],
        ({column: v, key: (n / total if normalize else n)} for v, n in counts),
    )


def group_by(table: Table, by: str | Sequence[str], aggregations: Mapping[str, str | Aggregator | Sequence[str | Aggregator]]) -> Table:
    """Group rows by ``by`` and aggregate other columns.

    ``aggregations`` maps a column to one or more aggregations, each either a
    name from :data:`AGGREGATIONS` or a callable taking the list of
    non-missing values. Output columns are named ``<column>_<aggregation>``.
    Groups appear in order of first occurrence.

        group_by(t, "region", {"sales": ["sum", "mean"], "id": "count"})
    """
    keys = [by] if isinstance(by, str) else list(by)
    table.select(keys + list(aggregations))

    specs: list[tuple[str, str, Aggregator]] = []
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

    groups: dict[tuple, list[dict]] = {}
    for row in table:
        groups.setdefault(tuple(_hashable(row[k]) for k in keys), []).append(row)

    out = []
    for key, rows in groups.items():
        result = dict(zip(keys, key))
        for col, name, fn in specs:
            result[name] = fn([r[col] for r in rows if r[col] is not None])
        out.append(result)
    return Table(keys + [name for _, name, _ in specs], out)


def correlation(table: Table, x: str, y: str) -> float | None:
    """Pearson correlation of two numeric columns over rows where both are present.

    Returns ``None`` if fewer than two such rows exist or either column is constant.
    """
    pairs = [(r[x], r[y]) for r in table if r[x] is not None and r[y] is not None]
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    if not (is_numeric(xs) and is_numeric(ys)):
        raise TypeError(f"correlation requires numeric columns: {x!r}, {y!r}")
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return None


def correlation_matrix(table: Table, columns: Sequence[str] | None = None) -> Table:
    """Pairwise Pearson correlations between numeric columns."""
    if columns is None:
        columns = [c for c in table.columns if is_numeric(table.column(c))]
    out = []
    for a in columns:
        row: dict[str, Any] = {"column": a}
        for b in columns:
            row[b] = 1.0 if a == b else correlation(table, a, b)
        out.append(row)
    return Table(["column", *columns], out)


def missing_report(table: Table) -> Table:
    """Count and fraction of missing values per column."""
    n = len(table)
    out = []
    for col in table.columns:
        missing = sum(v is None for v in table.column(col))
        out.append({"column": col, "missing": missing, "fraction": missing / n if n else 0.0})
    return Table(["column", "missing", "fraction"], out)


def _quartiles(values: list[float]) -> tuple[float, float, float]:
    if len(values) == 1:
        return values[0], values[0], values[0]
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return q1, q2, q3


def format_table(table: Table, *, precision: int = 3, max_rows: int = 50) -> str:
    """Render a table as aligned plain text for printing."""

    def fmt(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, float):
            return "nan" if math.isnan(v) else f"{v:.{precision}f}".rstrip("0").rstrip(".")
        return str(v)

    rows = [[fmt(r[c]) for c in table.columns] for r in table.head(max_rows)]
    widths = [max([len(c)] + [len(r[i]) for r in rows]) for i, c in enumerate(table.columns)]
    lines = ["  ".join(c.ljust(w) for c, w in zip(table.columns, widths))]
    lines.append("  ".join("-" * w for w in widths))
    lines += ["  ".join(v.ljust(w) for v, w in zip(r, widths)) for r in rows]
    if len(table) > max_rows:
        lines.append(f"... ({len(table) - max_rows} more rows)")
    return "\n".join(lines)
