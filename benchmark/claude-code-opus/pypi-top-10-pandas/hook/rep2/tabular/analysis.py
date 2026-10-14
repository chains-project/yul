"""Summary statistics and aggregation."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from statistics import StatisticsError, mean, median, quantiles, stdev
from typing import Any

from tabular.table import Table

Aggregation = str | Callable[[list[Any]], Any]

_AGGREGATIONS: dict[str, Callable[[list[Any]], Any]] = {
    "count": len,
    "sum": sum,
    "mean": mean,
    "median": median,
    "min": min,
    "max": max,
    "std": lambda values: stdev(values) if len(values) > 1 else None,
    "nunique": lambda values: len(set(values)),
}


def is_numeric(values: Sequence[Any]) -> bool:
    """True if every non-missing value is an int or float (bools excluded)."""
    present = [v for v in values if v is not None]
    return bool(present) and all(_is_number(v) for v in present)


def describe(table: Table) -> Table:
    """Summarize each column, one row per column.

    Every column gets ``count`` (non-missing), ``missing``, and ``unique``.
    Numeric columns add mean, std, min, 25%, 50%, 75%, max; other columns add
    ``top`` (most frequent value) and ``freq``.
    """
    rows = []
    for name in table.columns:
        column = table[name]
        present = [v for v in column if v is not None]
        row: dict[str, Any] = {
            "column": name,
            "count": len(present),
            "missing": len(column) - len(present),
            "unique": len(set(present)),
        }
        if is_numeric(column):
            q1, q2, q3 = _quartiles(present)
            row.update(
                mean=mean(present),
                std=stdev(present) if len(present) > 1 else None,
                min=min(present),
                **{"25%": q1, "50%": q2, "75%": q3},
                max=max(present),
            )
        elif present:
            top, freq = Counter(present).most_common(1)[0]
            row.update(top=top, freq=freq)
        rows.append(row)
    order = ["column", "count", "missing", "unique", "mean", "std", "min", "25%", "50%", "75%", "max", "top", "freq"]
    present_keys = {key for row in rows for key in row}
    return Table.from_rows(rows, [key for key in order if key in present_keys])


def value_counts(table: Table, column: str, *, dropna: bool = True, normalize: bool = False) -> Table:
    """Count occurrences of each value in ``column``, most frequent first."""
    values = table[column]
    if dropna:
        values = [v for v in values if v is not None]
    counts = Counter(values).most_common()
    total = len(values)
    key = "proportion" if normalize else "count"
    return Table({
        column: [value for value, _ in counts],
        key: [n / total if normalize else n for _, n in counts],
    })


def group_by(table: Table, by: str | Sequence[str], aggregations: Mapping[str, Aggregation | Sequence[Aggregation]]) -> Table:
    """Group rows by one or more key columns and aggregate other columns.

    ``aggregations`` maps a column to an aggregation name ("count", "sum",
    "mean", "median", "min", "max", "std", "nunique"), a callable taking the
    group's non-missing values, or a list of these. Output columns are named
    ``<column>_<aggregation>``. Groups keep first-seen order; rows with a
    missing key are kept as their own ``None`` group.

        group_by(sales, "region", {"amount": ["sum", "mean"]})
    """
    keys = [by] if isinstance(by, str) else list(by)
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in table.rows():
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)

    specs: list[tuple[str, str, Callable[[list[Any]], Any]]] = []
    for column, aggs in aggregations.items():
        if column not in table:
            raise KeyError(f"unknown column: {column!r}")
        if isinstance(aggs, str) or callable(aggs):
            aggs = [aggs]
        for agg in aggs:
            if isinstance(agg, str):
                if agg not in _AGGREGATIONS:
                    raise ValueError(f"unknown aggregation {agg!r}; expected one of {sorted(_AGGREGATIONS)}")
                specs.append((f"{column}_{agg}", column, _AGGREGATIONS[agg]))
            else:
                specs.append((f"{column}_{getattr(agg, '__name__', 'agg')}", column, agg))

    out_rows = []
    for key, rows in groups.items():
        out = dict(zip(keys, key))
        for out_name, column, func in specs:
            values = [r[column] for r in rows if r[column] is not None]
            try:
                out[out_name] = func(values) if values or func is len else None
            except (StatisticsError, TypeError):
                out[out_name] = None
        out_rows.append(out)
    return Table.from_rows(out_rows, keys + [name for name, _, _ in specs])


def correlation(table: Table, columns: Sequence[str] | None = None) -> Table:
    """Pearson correlation matrix for numeric columns, using pairwise-complete rows."""
    names = list(columns) if columns is not None else [n for n in table.columns if is_numeric(table[n])]
    data = {n: table[n] for n in names}
    matrix: dict[str, list[Any]] = {"column": names}
    for b in names:
        matrix[b] = [_pearson(data[a], data[b]) for a in names]
    return Table(matrix)


def _pearson(xs: Sequence[Any], ys: Sequence[Any]) -> float | None:
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 2:
        return None
    mx = sum(x for x, _ in pairs) / len(pairs)
    my = sum(y for _, y in pairs) / len(pairs)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    syy = sum((y - my) ** 2 for _, y in pairs)
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _quartiles(values: list[Any]) -> tuple[Any, Any, Any]:
    if len(values) == 1:
        return values[0], values[0], values[0]
    q1, q2, q3 = quantiles(values, n=4, method="inclusive")
    return q1, q2, q3


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
