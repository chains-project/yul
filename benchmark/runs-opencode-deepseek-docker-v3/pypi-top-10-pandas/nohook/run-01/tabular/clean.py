"""Cleaning and normalisation operations.

Every function returns a new :class:`~tabular.table.Table`; the input table is
never modified.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Iterable, List, Mapping, Optional, Sequence

from .io import coerce_value
from .table import Table

_NON_WORD = re.compile(r"[^\w]+")

# Aggregation helpers -------------------------------------------------------

def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _mode(values: Sequence[Any]) -> Any:
    counts: dict = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return None
    return max(counts, key=counts.get)


# Operations ----------------------------------------------------------------

def strip_whitespace(table: Table, columns: Optional[Sequence[str]] = None) -> Table:
    """Strip leading/trailing whitespace from string cells."""
    targets = table.columns if columns is None else list(columns)
    for name in targets:
        if name not in table:
            raise KeyError(f"unknown column: {name!r}")
    data = {}
    for name in table.columns:
        values = table.column(name)
        if name in targets:
            values = [value.strip() if isinstance(value, str) else value for value in values]
        data[name] = values
    return Table(table.columns, data)


def normalize_column_names(table: Table, case: str = "lower") -> Table:
    """Normalise column names to ``snake_case``, de-duplicating as needed.

    ``case`` may be ``"lower"``, ``"upper"`` or ``None``.
    """
    rename: dict = {}
    used: dict = {}
    for name in table.columns:
        cleaned = _NON_WORD.sub("_", str(name).strip()).strip("_")
        if not cleaned:
            cleaned = "column"
        if case == "lower":
            cleaned = cleaned.lower()
        elif case == "upper":
            cleaned = cleaned.upper()
        elif case is not None:
            raise ValueError("case must be 'lower', 'upper' or None")
        candidate = cleaned
        if candidate in used:
            used[candidate] += 1
            candidate = f"{cleaned}_{used[candidate]}"
        used.setdefault(candidate, 0)
        rename[name] = candidate
    return table.rename(rename)


def drop_missing(
    table: Table,
    columns: Optional[Sequence[str]] = None,
    how: str = "any",
) -> Table:
    """Drop rows containing missing values.

    ``how`` is ``"any"`` (drop when any selected value is missing) or ``"all"``
    (drop only when all selected values are missing).
    """
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    targets = table.columns if columns is None else list(columns)
    for name in targets:
        if name not in table:
            raise KeyError(f"unknown column: {name!r}")

    keep = []
    for row in table.rows(named=True):
        missing = [row[name] is None for name in targets]
        should_drop = any(missing) if how == "any" else all(missing)
        if not should_drop:
            keep.append(row)
    return Table.from_dicts(keep, columns=table.columns)


def fill_missing(
    table: Table,
    value: Any = None,
    columns: Optional[Sequence[str]] = None,
    strategy: str = "value",
) -> Table:
    """Fill missing values.

    Strategies:

    ``"value"``
        Replace missing values with ``value``.
    ``"mean"`` / ``"median"``
        Replace with the column mean/median (numeric columns only).
    ``"mode"``
        Replace with the most common non-missing value.
    ``"ffill"`` / ``"bfill"``
        Forward/backward fill within the column.
    """
    valid = {"value", "mean", "median", "mode", "ffill", "bfill"}
    if strategy not in valid:
        raise ValueError(f"strategy must be one of {sorted(valid)!r}")
    targets = table.columns if columns is None else list(columns)
    for name in targets:
        if name not in table:
            raise KeyError(f"unknown column: {name!r}")

    data = {}
    for name in table.columns:
        values = table.column(name)
        if name not in targets:
            data[name] = values
            continue
        data[name] = _fill_column(values, value, strategy)
    return Table(table.columns, data)


def _fill_column(values: List[Any], value: Any, strategy: str) -> List[Any]:
    present = [v for v in values if v is not None]
    if strategy == "value":
        replacement = value
    elif strategy == "mode":
        replacement = _mode(present)
    elif strategy in ("mean", "median"):
        numeric = [v for v in present if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if not numeric:
            raise ValueError(f"cannot compute {strategy} of non-numeric column")
        replacement = _mean(numeric) if strategy == "mean" else _median(numeric)
    elif strategy == "ffill":
        result = []
        last = value
        for item in values:
            if item is None:
                result.append(last)
            else:
                result.append(item)
                last = item
        return result
    else:  # bfill
        result = []
        last = value
        for item in reversed(values):
            if item is None:
                result.append(last)
            else:
                result.append(item)
                last = item
        return list(reversed(result))

    return [replacement if item is None else item for item in values]


def drop_duplicates(
    table: Table,
    columns: Optional[Sequence[str]] = None,
    keep: str = "first",
) -> Table:
    """Remove duplicate rows.

    ``keep`` is ``"first"``, ``"last"`` or ``False`` (drop every duplicated
    row).
    """
    targets = table.columns if columns is None else list(columns)
    for name in targets:
        if name not in table:
            raise KeyError(f"unknown column: {name!r}")
    if keep not in ("first", "last", False, None):
        raise ValueError("keep must be 'first', 'last' or False")

    indexed = []
    seen: dict = {}
    for position, row in enumerate(table.rows(named=True)):
        key = tuple(row[name] for name in targets)
        indexed.append((key, position, row))
        seen.setdefault(key, []).append(position)

    keep_positions = set()
    for key, positions in seen.items():
        if len(positions) == 1:
            keep_positions.add(positions[0])
        elif keep == "first":
            keep_positions.add(positions[0])
        elif keep == "last":
            keep_positions.add(positions[-1])
        # keep in (False, None) -> drop every duplicated position

    ordered = sorted(keep_positions)
    return Table.from_dicts([indexed[i][2] for i in ordered], columns=table.columns)


def convert_types(table: Table, schema: Mapping[str, str]) -> Table:
    """Convert columns to the types described by ``schema``.

    ``schema`` maps a column name to one of ``"str"``, ``"int"``, ``"float"``,
    ``"bool"`` or ``"auto"``.
    """
    unknown = set(schema).difference(table.columns)
    if unknown:
        raise KeyError(f"unknown columns: {sorted(unknown)!r}")
    data = {}
    for name in table.columns:
        values = table.column(name)
        if name in schema:
            values = [coerce_value(value, schema[name]) for value in values]
        data[name] = values
    return Table(table.columns, data)


def replace_values(
    table: Table,
    replacements: Mapping[Any, Any],
    columns: Optional[Sequence[str]] = None,
) -> Table:
    """Replace values in ``columns`` according to ``replacements``."""
    targets = table.columns if columns is None else list(columns)
    for name in targets:
        if name not in table:
            raise KeyError(f"unknown column: {name!r}")
    data = {}
    for name in table.columns:
        values = table.column(name)
        if name in targets:
            values = [replacements.get(value, value) for value in values]
        data[name] = values
    return Table(table.columns, data)


def filter_rows(table: Table, predicate: Callable[[Mapping[str, Any]], bool]) -> Table:
    """Keep only rows for which ``predicate`` returns a truthy value."""
    return Table.from_dicts(
        [row for row in table.rows(named=True) if predicate(row)],
        columns=table.columns,
    )
