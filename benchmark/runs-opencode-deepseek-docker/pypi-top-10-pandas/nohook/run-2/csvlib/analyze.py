"""Analysis helpers for :class:`~csvlib.table.Table`."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from statistics import mean, median, stdev
from typing import Any, Optional, Union

from ._utils import is_missing, resolve_columns
from .table import Table

Aggregator = Union[str, Callable[[list[Any]], Any]]

_AGGREGATORS: dict[str, Callable[[list[Any]], Any]] = {
    "count": len,
    "sum": lambda values: sum(values) if values else None,
    "mean": lambda values: mean(values) if values else None,
    "median": lambda values: median(values) if values else None,
    "min": lambda values: min(values) if values else None,
    "max": lambda values: max(values) if values else None,
    "std": lambda values: stdev(values) if len(values) > 1 else None,
}
_NUMERIC_AGGREGATORS = frozenset({"sum", "mean", "median", "min", "max", "std"})


def _to_number(value: Any) -> Optional[float]:
    """Best-effort conversion to ``float``, or ``None`` when not numeric."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _present(values: Iterable[Any]) -> list[Any]:
    return [value for value in values if not is_missing(value)]


def is_numeric_column(table: Table, column: str) -> bool:
    """Return ``True`` if every non-missing value of *column* is numeric."""
    present = _present(table.column(column))
    return bool(present) and all(_to_number(value) is not None for value in present)


def numeric_columns(table: Table) -> list[str]:
    """Names of columns that are entirely numeric (ignoring missing values)."""
    return [column for column in table.columns if is_numeric_column(table, column)]


def categorical_columns(table: Table) -> list[str]:
    """Names of non-numeric columns that contain at least one value."""
    return [
        column
        for column in table.columns
        if not is_numeric_column(table, column) and _present(table.column(column))
    ]


def missing_report(table: Table) -> dict[str, dict[str, Any]]:
    """Per-column counts of missing and present values."""
    total = table.num_rows
    report: dict[str, dict[str, Any]] = {}
    for column in table.columns:
        missing = sum(1 for value in table.column(column) if is_missing(value))
        report[column] = {
            "missing": missing,
            "present": total - missing,
            "fraction": missing / total if total else 0.0,
        }
    return report


def value_counts(
    table: Table,
    column: str,
    *,
    normalize: bool = False,
    dropna: bool = True,
) -> dict[Any, float]:
    """Count occurrences of each distinct value in *column*.

    Results are ordered by descending count (ties broken by value).  When
    *normalize* is true the values are relative frequencies.
    """
    resolve_columns(table, [column])
    values = table.column(column)
    if dropna:
        values = _present(values)
    counts = Counter(values)
    total = sum(counts.values())
    ordered = sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))
    if normalize:
        return {value: (count / total if total else 0.0) for value, count in ordered}
    return {value: count for value, count in ordered}


def column_stats(table: Table, column: str) -> dict[str, Any]:
    """Compute descriptive statistics for a single *column*."""
    resolve_columns(table, [column])
    values = table.column(column)
    present = _present(values)
    stats: dict[str, Any] = {
        "column": column,
        "count": len(present),
        "missing": len(values) - len(present),
        "unique": len(set(map(_hashable, present))),
    }
    if is_numeric_column(table, column):
        numbers = [_to_number(value) for value in present]
        numbers = [number for number in numbers if number is not None]
        stats.update(
            min=min(numbers),
            max=max(numbers),
            mean=mean(numbers),
            median=median(numbers),
            std=stdev(numbers) if len(numbers) > 1 else 0.0,
        )
    elif present:
        counts = Counter(present)
        top, freq = sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))[0]
        stats["top"] = top
        stats["freq"] = freq
    return stats


def describe(table: Table, columns: Optional[Any] = None) -> dict[str, dict[str, Any]]:
    """Return ``{column: stats}`` for every selected column."""
    selected = resolve_columns(table, columns)
    return {column: column_stats(table, column) for column in selected}


def summary(table: Table) -> Table:
    """Return the per-column statistics from :func:`describe` as a table."""
    stats = describe(table)
    fields = ["column", "count", "missing", "unique", "mean", "std", "min", "max", "top", "freq"]
    rows = [[record.get(field) for field in fields] for record in stats.values()]
    return Table(fields, rows)


def correlation(table: Table, column_a: str, column_b: str) -> Optional[float]:
    """Pearson correlation between two columns, or ``None`` if undefined."""
    resolve_columns(table, [column_a, column_b])
    pairs = []
    for row in table:
        a = _to_number(row[column_a])
        b = _to_number(row[column_b])
        if a is None or b is None:
            continue
        pairs.append((a, b))
    if len(pairs) < 2:
        return None
    mean_a = mean(a for a, _ in pairs)
    mean_b = mean(b for _, b in pairs)
    cov = sum((a - mean_a) * (b - mean_b) for a, b in pairs)
    var_a = sum((a - mean_a) ** 2 for a, _ in pairs)
    var_b = sum((b - mean_b) ** 2 for _, b in pairs)
    if var_a == 0 or var_b == 0:
        return None
    return cov / math.sqrt(var_a * var_b)


def group_by(
    table: Table,
    keys: Union[str, Sequence[str]],
    aggregations: Mapping[str, tuple[str, Aggregator]],
) -> Table:
    """Group rows by *keys* and aggregate.

    *aggregations* maps an output column name to ``(source_column, aggregator)``
    where *aggregator* is a callable or one of ``count``, ``sum``, ``mean``,
    ``median``, ``min``, ``max``, ``std``.
    """
    key_columns = [keys] if isinstance(keys, str) else list(keys)
    resolve_columns(table, key_columns)
    if not aggregations:
        raise ValueError("aggregations must not be empty")

    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    order: list[tuple[Any, ...]] = []
    for row in table:
        key = tuple(_hashable(row[column]) for column in key_columns)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    out_columns = key_columns + list(aggregations)
    rows = []
    for key in order:
        members = groups[key]
        record: dict[str, Any] = dict(zip(key_columns, key))
        for name, spec in aggregations.items():
            if not (isinstance(spec, (tuple, list)) and len(spec) == 2):
                raise ValueError(
                    f"aggregation {name!r} must be a (column, aggregator) pair"
                )
            source, aggregator = spec
            resolve_columns(table, [source])
            values = [row[source] for row in members if not is_missing(row[source])]
            record[name] = _apply_aggregator(aggregator, values)
        rows.append(record)
    return Table(out_columns, rows)


def _apply_aggregator(aggregator: Aggregator, values: list[Any]) -> Any:
    if callable(aggregator):
        return aggregator(values)
    if aggregator not in _AGGREGATORS:
        raise ValueError(
            f"unknown aggregator {aggregator!r}; expected one of "
            f"{sorted(_AGGREGATORS)} or a callable"
        )
    if aggregator in _NUMERIC_AGGREGATORS:
        numbers = [_to_number(value) for value in values]
        if any(number is None for number in numbers):
            raise ValueError("aggregator requires numeric values")
        values = [number for number in numbers if number is not None]
    return _AGGREGATORS[aggregator](values)


def _hashable(value: Any) -> Any:
    try:
        hash(value)
    except TypeError:
        return repr(value)
    return value
