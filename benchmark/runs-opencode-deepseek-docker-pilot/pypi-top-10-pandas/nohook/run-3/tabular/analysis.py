"""Summary statistics and exploratory analysis for :class:`Table` objects."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from collections.abc import Sequence
from typing import Any

from .cleaning import DEFAULT_MISSING, looks_missing, normalize_missing, is_missing
from .table import Table


def to_number(value: Any) -> float | None:
    """Return ``value`` as a float, or ``None`` if it is not numeric."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if text == "":
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _numeric(values: Sequence[Any]) -> list[float]:
    numbers = []
    for value in values:
        number = to_number(value)
        if number is not None and not math.isnan(number):
            numbers.append(number)
    return numbers


def missing_report(
    table: Table, *, missing: Sequence[str] = tuple(DEFAULT_MISSING)
) -> dict[str, int]:
    """Return the number of missing values per column."""
    tokens = normalize_missing(missing)
    return {
        header: sum(
            1
            for value in table.column(header)
            if looks_missing(value, tokens)
        )
        for header in table.headers
    }


def numeric_summary(table: Table, column: str) -> dict[str, Any]:
    """Return descriptive statistics for a numeric column."""
    values = table.column(column)
    numbers = _numeric(values)
    summary: dict[str, Any] = {
        "column": column,
        "count": len(numbers),
        "missing": len(values) - len(numbers),
    }
    if not numbers:
        return summary

    summary.update(
        {
            "mean": statistics.fmean(numbers),
            "median": statistics.median(numbers),
            "stdev": statistics.stdev(numbers) if len(numbers) > 1 else 0.0,
            "minimum": min(numbers),
            "maximum": max(numbers),
            "total": math.fsum(numbers),
        }
    )
    return summary


def describe(table: Table) -> dict[str, dict[str, Any]]:
    """Return a per-column summary.

    Numeric columns get descriptive statistics; other columns get cardinality
    information.
    """
    report: dict[str, dict[str, Any]] = {}
    for header in table.headers:
        values = table.column(header)
        numbers = _numeric(values)
        if values and len(numbers) == len(values):
            report[header] = numeric_summary(table, header)
        else:
            counter = Counter(value for value in values if not is_missing(value))
            most_common = counter.most_common(1)
            report[header] = {
                "column": header,
                "count": len(values) - sum(
                    1 for value in values if is_missing(value)
                ),
                "unique": len(counter),
                "top": most_common[0][0] if most_common else None,
                "freq": most_common[0][1] if most_common else 0,
            }
    return report


def value_counts(
    table: Table,
    column: str,
    *,
    top: int | None = None,
    normalize: bool = False,
) -> list[tuple[Any, float]]:
    """Return ``(value, count)`` pairs ordered from most to least frequent."""
    counter = Counter(
        value for value in table.column(column) if not is_missing(value)
    )
    items = counter.most_common(top)
    total = sum(counter.values())
    if normalize and total:
        return [(value, count / total) for value, count in items]
    return [(value, count) for value, count in items]


def correlation(table: Table, column_a: str, column_b: str) -> float | None:
    """Return the Pearson correlation between two columns.

    Returns ``None`` when the correlation is undefined (fewer than two paired
    numeric values, or no variance in one of the columns).
    """
    pairs = []
    for left, right in zip(table.column(column_a), table.column(column_b)):
        left_number = to_number(left)
        right_number = to_number(right)
        if left_number is not None and right_number is not None:
            pairs.append((left_number, right_number))

    if len(pairs) < 2:
        return None

    count = len(pairs)
    mean_a = sum(left for left, _ in pairs) / count
    mean_b = sum(right for _, right in pairs) / count
    covariance = sum(
        (left - mean_a) * (right - mean_b) for left, right in pairs
    )
    variance_a = sum((left - mean_a) ** 2 for left, _ in pairs)
    variance_b = sum((right - mean_b) ** 2 for _, right in pairs)

    if variance_a == 0 or variance_b == 0:
        return None
    return covariance / math.sqrt(variance_a * variance_b)


def infer_types(table: Table) -> dict[str, str]:
    """Classify each column as ``"numeric"``, ``"boolean"``, ``"text"`` or
    ``"empty"``."""
    types: dict[str, str] = {}
    for header in table.headers:
        values = [value for value in table.column(header) if not is_missing(value)]
        if not values:
            types[header] = "empty"
        elif all(isinstance(value, bool) for value in values) or all(
            str(value).strip().lower() in {"true", "false", "yes", "no"}
            for value in values
        ):
            types[header] = "boolean"
        elif all(to_number(value) is not None for value in values):
            types[header] = "numeric"
        else:
            types[header] = "text"
    return types
