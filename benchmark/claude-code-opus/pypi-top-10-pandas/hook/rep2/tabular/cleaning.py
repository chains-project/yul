"""Cleaning operations. Each takes a Table and returns a new Table."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from statistics import mean, median, mode
from typing import Any

from tabular.table import Table

FillStrategy = str  # "mean" | "median" | "mode"
_STRATEGIES: dict[str, Callable[[list[Any]], Any]] = {"mean": mean, "median": median, "mode": mode}


def strip_whitespace(table: Table) -> Table:
    """Trim surrounding whitespace from strings; strings that become empty turn into ``None``."""
    def strip(value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    return Table({name: [strip(v) for v in table[name]] for name in table.columns})


def normalize_column_names(table: Table) -> Table:
    """Convert column names to ``snake_case`` identifiers, e.g. ``"Unit Price ($)"`` -> ``"unit_price"``."""
    mapping: dict[str, str] = {}
    used: set[str] = set()
    for name in table.columns:
        snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        snake = re.sub(r"[^0-9a-zA-Z]+", "_", snake).strip("_").lower() or "column"
        if snake[0].isdigit():
            snake = f"_{snake}"
        candidate, n = snake, 1
        while candidate in used:
            n += 1
            candidate = f"{snake}_{n}"
        used.add(candidate)
        mapping[name] = candidate
    return table.rename(mapping)


def drop_duplicates(table: Table, subset: Sequence[str] | None = None) -> Table:
    """Remove repeated rows, keeping the first. ``subset`` limits which columns are compared."""
    keys = list(subset) if subset is not None else table.columns
    seen: set[tuple[Any, ...]] = set()
    kept = []
    for row in table.rows():
        key = tuple(_hashable(row[k]) for k in keys)
        if key not in seen:
            seen.add(key)
            kept.append(row)
    return Table.from_rows(kept, table.columns)


def drop_missing(table: Table, subset: Sequence[str] | None = None, *, how: str = "any") -> Table:
    """Drop rows with missing values in ``subset`` (default: all columns).

    ``how="any"`` drops a row if any checked value is missing; ``how="all"``
    only if every checked value is.
    """
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    keys = list(subset) if subset is not None else table.columns
    test = any if how == "any" else all
    return table.filter(lambda row: not test(row[k] is None for k in keys))


def drop_empty_columns(table: Table) -> Table:
    """Remove columns whose values are all missing."""
    return table.select(*(n for n in table.columns if any(v is not None for v in table[n])))


def fill_missing(table: Table, values: Any | Mapping[str, Any] = None, *, strategy: FillStrategy | None = None) -> Table:
    """Replace missing values.

    Pass a single ``values`` for every column, a mapping of column -> value,
    or a ``strategy`` ("mean", "median", "mode") computed per column.
    Mean and median apply only to numeric columns; others are left as-is.
    """
    if (values is None) == (strategy is None):
        raise ValueError("pass exactly one of values or strategy")
    if strategy is not None and strategy not in _STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; expected one of {sorted(_STRATEGIES)}")

    columns = {}
    for name in table.columns:
        column = table[name]
        present = [v for v in column if v is not None]
        if strategy is not None:
            if not present or (strategy != "mode" and not all(_is_number(v) for v in present)):
                columns[name] = column
                continue
            fill = _STRATEGIES[strategy](present)
        elif isinstance(values, Mapping):
            if name not in values:
                columns[name] = column
                continue
            fill = values[name]
        else:
            fill = values
        columns[name] = [fill if v is None else v for v in column]
    return Table(columns)


def clean(table: Table) -> Table:
    """Apply the standard cleaning pipeline: normalize names, strip whitespace,
    drop all-empty rows and columns, then drop duplicate rows."""
    table = normalize_column_names(table)
    table = strip_whitespace(table)
    table = drop_missing(table, how="all")
    table = drop_empty_columns(table)
    return drop_duplicates(table)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _hashable(value: Any) -> Any:
    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)
