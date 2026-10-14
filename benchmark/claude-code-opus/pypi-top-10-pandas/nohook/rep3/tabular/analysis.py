"""Statistics over table columns. Missing values (``None``) are ignored."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from datetime import date, datetime
from typing import Any, Iterable


def _present(values: Iterable[Any]) -> list:
    return [v for v in values if v is not None]


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_numeric(values: Iterable[Any]) -> bool:
    """True if the column has at least one value and all values are numbers."""
    present = _present(values)
    return bool(present) and all(_is_number(v) for v in present)


def column_type(values: Iterable[Any]) -> str:
    """Name of the Python type held by a column (``"mixed"`` if several)."""
    kinds = set()
    for v in _present(values):
        if isinstance(v, bool):
            kinds.add("bool")
        elif isinstance(v, int):
            kinds.add("int")
        elif isinstance(v, float):
            kinds.add("float")
        elif isinstance(v, datetime):
            kinds.add("datetime")
        elif isinstance(v, date):
            kinds.add("date")
        else:
            kinds.add(type(v).__name__)
    if kinds == {"int", "float"}:
        return "float"
    if len(kinds) == 1:
        return kinds.pop()
    return "mixed" if kinds else "empty"


def value_counts(values: Iterable[Any], *, dropna: bool = True) -> dict[Any, int]:
    """Distinct values mapped to their counts, most common first."""
    values = _present(values) if dropna else list(values)
    return dict(Counter(values).most_common())


def quantile(values: Iterable[Any], q: float) -> float | None:
    """Linear-interpolated quantile, ``0 <= q <= 1``."""
    data = sorted(_present(values))
    if not data:
        return None
    pos = (len(data) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return data[lo] + (data[hi] - data[lo]) * (pos - lo)


def aggregate(values: Iterable[Any], agg: str) -> Any:
    values = list(values)
    data = _present(values)
    if agg == "count":
        return len(data)
    if agg == "nunique":
        return len(set(data))
    if agg == "first":
        return data[0] if data else None
    if agg == "last":
        return data[-1] if data else None
    if agg not in ("sum", "mean", "median", "min", "max", "std"):
        raise ValueError(f"unknown aggregation {agg!r}")
    if not data:
        return None
    if agg == "min":
        return min(data)
    if agg == "max":
        return max(data)
    if not all(_is_number(v) for v in data):
        raise TypeError(f"{agg!r} requires a numeric column")
    if agg == "sum":
        return sum(data)
    if agg == "mean":
        return statistics.fmean(data)
    if agg == "median":
        return statistics.median(data)
    return statistics.stdev(data) if len(data) > 1 else None


def describe(name: str, values: list) -> dict[str, Any]:
    """Summary of one column.

    Every column gets ``count``, ``missing``, ``unique``, ``top`` and
    ``freq``. Numeric columns also get ``mean``, ``std``, ``min``, ``25%``,
    ``50%``, ``75%``, ``max``; dates get ``min`` and ``max``.
    """
    data = _present(values)
    counts = Counter(data)
    top, freq = counts.most_common(1)[0] if counts else (None, None)
    row: dict[str, Any] = {
        "column": name,
        "type": column_type(values),
        "count": len(data),
        "missing": len(values) - len(data),
        "unique": len(counts),
        "top": top,
        "freq": freq,
    }
    if is_numeric(data):
        row.update({
            "mean": aggregate(data, "mean"),
            "std": aggregate(data, "std"),
            "min": min(data),
            "25%": quantile(data, 0.25),
            "50%": quantile(data, 0.5),
            "75%": quantile(data, 0.75),
            "max": max(data),
        })
    elif data and all(isinstance(v, date) for v in data):
        row.update({"min": min(data), "max": max(data)})
    return row


def outlier_mask(values: list, *, method: str = "iqr",
                 threshold: float | None = None) -> list[bool]:
    """``True`` where a numeric value is an outlier; ``None`` is never one."""
    data = _present(values)
    if not is_numeric(data):
        raise TypeError("outlier detection requires a numeric column")
    if method == "iqr":
        k = 1.5 if threshold is None else threshold
        q1, q3 = quantile(data, 0.25), quantile(data, 0.75)
        lo, hi = q1 - k * (q3 - q1), q3 + k * (q3 - q1)
        return [v is not None and not lo <= v <= hi for v in values]
    if method == "zscore":
        k = 3.0 if threshold is None else threshold
        if len(data) < 2:
            return [False] * len(values)
        mean, sd = statistics.fmean(data), statistics.stdev(data)
        if sd == 0:
            return [False] * len(values)
        return [v is not None and abs(v - mean) / sd > k for v in values]
    raise ValueError(f"unknown outlier method {method!r}")


def _ranks(data: list[float]) -> list[float]:
    """Ranks starting at 1, ties get the average rank."""
    order = sorted(range(len(data)), key=data.__getitem__)
    ranks = [0.0] * len(data)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and data[order[j + 1]] == data[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def correlation(x: list, y: list, method: str = "pearson") -> float | None:
    """Correlation over rows where both values are present.

    Returns ``None`` with fewer than two such rows or zero variance.
    """
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 2:
        return None
    xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
    if method == "spearman":
        xs, ys = _ranks(xs), _ranks(ys)
    elif method != "pearson":
        raise ValueError(f"unknown correlation method {method!r}")
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return None
