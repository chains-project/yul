"""Cleaning operations for :class:`csvlab.table.Table`.

Every function returns a new table and never mutates its input.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from ._common import is_number

_FORWARD = {"forward", "ffill"}
_BACKWARD = {"backward", "bfill"}
_VALID_STRATEGIES = {
    "mean",
    "median",
    "mode",
    "zero",
    "min",
    "max",
    *_FORWARD,
    *_BACKWARD,
}


def _new(
    table: Any,
    rows: Iterable[Mapping[str, Any]],
    columns: Sequence[str] | None = None,
) -> Any:
    return table.__class__(columns if columns is not None else table.columns, rows)


def _resolve_columns(table: Any, columns: Sequence[str] | None) -> list[str]:
    if columns is None:
        return list(table.columns)
    resolved = list(columns)
    unknown = [c for c in resolved if c not in table.columns]
    if unknown:
        raise KeyError(f"unknown columns: {unknown}")
    return resolved


def drop_duplicates(table: Any, subset: Sequence[str] | None = None) -> Any:
    """Remove rows whose values in ``subset`` (default: all columns) repeat."""
    subset = _resolve_columns(table, subset)
    seen: set[tuple] = set()
    rows = []
    for row in table.rows:
        key = tuple(row.get(col) for col in subset)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return _new(table, rows)


def drop_missing(
    table: Any,
    *,
    how: str = "any",
    subset: Sequence[str] | None = None,
    threshold: float | None = None,
) -> Any:
    """Drop rows containing missing values.

    ``how="any"`` drops a row if any selected column is missing, ``"all"``
    only if every selected column is missing. Alternatively ``threshold``
    (0..1) keeps rows whose missing fraction is at most that value.
    """
    subset = _resolve_columns(table, subset)
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")

    rows = []
    for row in table.rows:
        missing = sum(1 for col in subset if row.get(col) is None)
        if threshold is not None:
            fraction = missing / len(subset) if subset else 0.0
            if fraction <= threshold:
                rows.append(row)
        elif how == "any":
            if missing == 0:
                rows.append(row)
        else:  # all
            if missing < len(subset):
                rows.append(row)
    return _new(table, rows)


def _strategy_value(present: list[Any], strategy: str) -> Any:
    from statistics import mean as _mean, median as _median

    if strategy == "mean":
        return _mean(present)
    if strategy == "median":
        return _median(present)
    if strategy == "min":
        return min(present)
    if strategy == "max":
        return max(present)
    if strategy == "zero":
        return 0
    if strategy == "mode":
        counts: dict[Any, int] = {}
        for value in present:
            counts[value] = counts.get(value, 0) + 1
        return max(counts, key=counts.get)
    raise ValueError(f"unknown fill strategy: {strategy!r}")


def fill_missing(
    table: Any,
    value: Any = None,
    *,
    columns: Sequence[str] | None = None,
    strategy: str | None = None,
) -> Any:
    """Fill missing values with ``value`` or a computed ``strategy``.

    Supported strategies: mean, median, mode, min, max, zero, forward,
    backward. Mean/median/min/max are skipped for non-numeric columns.
    """
    if strategy is not None and strategy not in _VALID_STRATEGIES:
        raise ValueError(f"unknown fill strategy: {strategy!r}")
    if value is None and strategy is None:
        raise ValueError("provide either value or strategy")

    resolved = _resolve_columns(table, columns)
    rows = [dict(row) for row in table.rows]

    for col in resolved:
        present = [row.get(col) for row in rows if row.get(col) is not None]

        if strategy in _FORWARD or strategy in _BACKWARD:
            ordered = rows if strategy in _FORWARD else list(reversed(rows))
            carry = None
            for row in ordered:
                current = row.get(col)
                if current is None:
                    row[col] = carry
                else:
                    carry = current
            continue

        if strategy in ("mean", "median", "min", "max"):
            numeric = [v for v in present if is_number(v)]
            if not numeric:
                continue
            fill = _strategy_value(numeric, strategy)
        elif strategy is not None:
            if not present:
                continue
            fill = _strategy_value(present, strategy)
        else:
            fill = value

        for row in rows:
            if row.get(col) is None:
                row[col] = fill

    return _new(table, rows)


def strip_whitespace(table: Any, columns: Sequence[str] | None = None) -> Any:
    """Trim surrounding whitespace from string values."""
    resolved = _resolve_columns(table, columns)
    rows = [dict(row) for row in table.rows]
    for row in rows:
        for col in resolved:
            value = row.get(col)
            if isinstance(value, str):
                row[col] = value.strip()
    return _new(table, rows)


def rename_columns(table: Any, mapping: Mapping[str, str]) -> Any:
    """Rename columns; unknown source names raise :class:`KeyError`."""
    unknown = [src for src in mapping if src not in table.columns]
    if unknown:
        raise KeyError(f"unknown columns: {unknown}")
    columns = [mapping.get(col, col) for col in table.columns]
    if len(set(columns)) != len(columns):
        raise ValueError("renaming would produce duplicate column names")
    rows = [
        {mapping.get(col, col): value for col, value in row.items()}
        for row in table.rows
    ]
    return _new(table, rows, columns)


def _normalize_name(name: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in name.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")


def normalize_headers(table: Any) -> Any:
    """Lowercase headers and replace non-alphanumeric characters with ``_``."""
    columns = [_normalize_name(col) for col in table.columns]
    if len(set(columns)) != len(columns):
        raise ValueError("normalizing headers would produce duplicate names")
    rows = [
        {_normalize_name(col): value for col, value in row.items()}
        for row in table.rows
    ]
    return _new(table, rows, columns)


def cast_column(table: Any, column: str, dtype: str) -> Any:
    """Cast a column to ``"int"``, ``"float"``, ``"str"``, or ``"bool"``.

    Missing values are preserved and unparseable values raise :class:`ValueError`.
    """
    if column not in table.columns:
        raise KeyError(column)
    caster = _CASTERS.get(dtype)
    if caster is None:
        raise ValueError(f"unknown dtype: {dtype!r}")

    rows = []
    for row in table.rows:
        row = dict(row)
        value = row.get(column)
        if value is not None:
            try:
                row[column] = caster(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"cannot convert {value!r} in column {column!r} to {dtype}"
                ) from exc
        rows.append(row)
    return _new(table, rows)


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "yes", "1"}:
        return True
    if text in {"false", "no", "0"}:
        return False
    raise ValueError(value)


_CASTERS = {
    "int": int,
    "float": float,
    "str": str,
    "bool": _to_bool,
}


def replace_values(table: Any, column: str, replacements: Mapping[Any, Any]) -> Any:
    """Replace specific values within a column."""
    if column not in table.columns:
        raise KeyError(column)
    rows = []
    for row in table.rows:
        row = dict(row)
        value = row.get(column)
        if value in replacements:
            row[column] = replacements[value]
        rows.append(row)
    return _new(table, rows)
