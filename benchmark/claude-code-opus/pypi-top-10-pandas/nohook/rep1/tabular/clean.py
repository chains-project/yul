"""Cleaning operations. Every function takes a Table and returns a new Table."""

from __future__ import annotations

import re
import statistics
from typing import Any, Callable, Sequence

from .table import Table


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and value != value)  # NaN check


def clean_column_names(table: Table) -> Table:
    """Normalize column names to ``snake_case`` identifiers.

    ``" Unit Price ($) "`` becomes ``"unit_price"``. Collisions get a numeric suffix.
    """
    seen: dict[str, int] = {}
    mapping = {}
    for col in table.columns:
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", col.strip())
        name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower() or "column"
        if name[0].isdigit():
            name = f"_{name}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        seen.setdefault(name, 0)
        mapping[col] = name
    return table.rename(mapping)


def strip_whitespace(table: Table) -> Table:
    """Strip leading/trailing whitespace from string cells; blank strings become missing."""
    def fix(v: Any) -> Any:
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v
    return Table({c: [fix(v) for v in table[c]] for c in table.columns})


def drop_duplicates(table: Table, subset: Sequence[str] | None = None) -> Table:
    """Keep the first occurrence of each row (or of each combination of ``subset`` columns)."""
    keys = list(subset or table.columns)
    seen = set()
    keep = []
    for i, row in enumerate(table.rows()):
        key = tuple(_hashable(row[k]) for k in keys)
        if key not in seen:
            seen.add(key)
            keep.append(i)
    return table.take(keep)


def _hashable(v: Any) -> Any:
    try:
        hash(v)
        return v
    except TypeError:
        return repr(v)


def drop_missing(table: Table, subset: Sequence[str] | None = None, how: str = "any") -> Table:
    """Drop rows with missing values.

    Args:
        subset: Columns to consider (default: all).
        how: ``"any"`` drops a row if any considered value is missing;
            ``"all"`` only if every considered value is missing.
    """
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    cols = list(subset or table.columns)
    test = any if how == "any" else all
    keep = [i for i, row in enumerate(table.rows()) if not test(_is_missing(row[c]) for c in cols)]
    return table.take(keep)


_STRATEGIES = ("mean", "median", "mode", "ffill", "bfill")


def fill_missing(
    table: Table,
    value: Any = None,
    strategy: str | None = None,
    columns: Sequence[str] | None = None,
) -> Table:
    """Fill missing values with a constant or a per-column strategy.

    Args:
        value: Constant to fill with, or a ``{column: value}`` dict.
        strategy: One of ``mean``, ``median``, ``mode``, ``ffill``, ``bfill``.
            ``mean``/``median`` skip non-numeric columns.
        columns: Restrict filling to these columns (default: all).
    """
    if (value is None) == (strategy is None):
        raise ValueError("specify exactly one of value or strategy")
    if strategy is not None and strategy not in _STRATEGIES:
        raise ValueError(f"strategy must be one of {_STRATEGIES}")

    targets = set(columns or table.columns)
    out = {}
    for col in table.columns:
        values = table[col]
        if col in targets:
            if strategy is None:
                fill = value.get(col) if isinstance(value, dict) else value
                if fill is not None:
                    values = [fill if _is_missing(v) else v for v in values]
            else:
                values = _apply_strategy(values, strategy)
        out[col] = values
    return Table(out)


def _apply_strategy(values: list[Any], strategy: str) -> list[Any]:
    if strategy in ("ffill", "bfill"):
        seq = values if strategy == "ffill" else values[::-1]
        last, filled = None, []
        for v in seq:
            if _is_missing(v):
                filled.append(last)
            else:
                last = v
                filled.append(v)
        return filled if strategy == "ffill" else filled[::-1]

    present = [v for v in values if not _is_missing(v)]
    if not present:
        return values
    if strategy == "mode":
        fill = statistics.mode(present)
    else:
        if not all(_is_number(v) for v in present):
            return values
        fill = statistics.fmean(present) if strategy == "mean" else statistics.median(present)
    return [fill if _is_missing(v) else v for v in values]


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def cast_column(table: Table, column: str, type_: Callable[[Any], Any], errors: str = "raise") -> Table:
    """Convert a column with ``type_`` (e.g. ``int``, ``float``, ``str``).

    Args:
        errors: ``"raise"`` to propagate conversion errors, ``"coerce"`` to
            replace unconvertible values with ``None``.
    """
    if errors not in ("raise", "coerce"):
        raise ValueError("errors must be 'raise' or 'coerce'")

    def convert(v: Any) -> Any:
        if _is_missing(v):
            return None
        try:
            return type_(v)
        except (ValueError, TypeError):
            if errors == "coerce":
                return None
            raise

    return table.with_column(column, [convert(v) for v in table[column]])


def filter_rows(table: Table, predicate: Callable[[dict[str, Any]], bool]) -> Table:
    """Keep rows for which ``predicate(row_dict)`` is true."""
    return table.take(i for i, row in enumerate(table.rows()) if predicate(row))
