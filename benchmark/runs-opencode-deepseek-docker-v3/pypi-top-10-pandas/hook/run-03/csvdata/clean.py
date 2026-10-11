"""Cleaning and normalization helpers for :class:`~csvdata.table.Table`."""

from __future__ import annotations

import re
from collections import Counter
from statistics import mean, median

from .table import Table, is_missing

_NON_WORD = re.compile(r"[^0-9a-zA-Z]+")


def strip_whitespace(table: Table, columns: list[str] | None = None) -> Table:
    """Trim leading/trailing whitespace from string cells."""
    target = set(columns) if columns is not None else None
    rows = []
    for row in table:
        new_row = {}
        for name, value in row.items():
            if isinstance(value, str) and (target is None or name in target):
                new_row[name] = value.strip()
            else:
                new_row[name] = value
        rows.append(new_row)
    return Table(table.columns, rows)


def normalize_headers(table: Table) -> Table:
    """Return a table whose column names are lower snake_case and unique."""
    mapping: dict[str, str] = {}
    used: set[str] = set()
    for index, name in enumerate(table.columns):
        slug = _NON_WORD.sub("_", name.strip().lower()).strip("_")
        if not slug:
            slug = f"column_{index + 1}"
        base = slug
        suffix = 1
        while slug in used:
            suffix += 1
            slug = f"{base}_{suffix}"
        used.add(slug)
        mapping[name] = slug
    rows = [{mapping[k]: v for k, v in row.items()} for row in table]
    return Table(list(mapping.values()), rows)


def _to_number(value):
    if is_missing(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    text = value.strip().replace(",", "")
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return None


def coerce_types(table: Table, columns: list[str] | None = None) -> Table:
    """Convert fully numeric columns to ``int``/``float``.

    A column is converted only when every non-missing value parses as a
    number, so mixed columns are left untouched.
    """
    target = list(columns) if columns is not None else table.columns
    conversions: dict[str, bool] = {}
    for name in target:
        values = [v for v in table.column(name) if not is_missing(v)]
        if values and all(_to_number(v) is not None for v in values):
            conversions[name] = True
        else:
            conversions[name] = False

    rows = []
    for row in table:
        new_row = {}
        for name, value in row.items():
            if conversions.get(name):
                new_row[name] = _to_number(value)
            else:
                new_row[name] = value
        rows.append(new_row)
    return Table(table.columns, rows)


def drop_missing(
    table: Table,
    *,
    subset: list[str] | None = None,
    how: str = "any",
) -> Table:
    """Drop rows containing missing values.

    *how* is ``"any"`` (drop if any selected cell is missing) or ``"all"``
    (drop only when every selected cell is missing).
    """
    if how not in {"any", "all"}:
        raise ValueError("how must be 'any' or 'all'")
    columns = subset if subset is not None else table.columns
    for name in columns:
        table.column(name)  # validate

    def keep(row: dict) -> bool:
        checks = [is_missing(row[name]) for name in columns]
        if not checks:
            return True
        return not all(checks) if how == "all" else not any(checks)

    return table.filter(keep)


def fill_missing(
    table: Table,
    *,
    value=None,
    strategy: str | None = None,
    columns: list[str] | None = None,
) -> Table:
    """Fill missing cells with a constant or a computed statistic.

    *strategy* may be ``"mean"``, ``"median"`` or ``"mode"``. When omitted,
    *value* is used as the constant fill.
    """
    if strategy is not None and strategy not in {"mean", "median", "mode"}:
        raise ValueError("strategy must be 'mean', 'median', 'mode' or None")
    target = list(columns) if columns is not None else table.columns

    fills: dict[str, object] = {}
    for name in target:
        present = [v for v in table.column(name) if not is_missing(v)]
        if strategy is None:
            fills[name] = value
        elif strategy == "mode":
            if present:
                fills[name] = Counter(present).most_common(1)[0][0]
            else:
                fills[name] = value
        else:
            numbers = [v for v in present if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if not numbers:
                fills[name] = value
            elif strategy == "mean":
                fills[name] = mean(numbers)
            else:
                fills[name] = median(numbers)

    rows = []
    for row in table:
        new_row = dict(row)
        for name in target:
            if is_missing(new_row[name]):
                new_row[name] = fills[name]
        rows.append(new_row)
    return Table(table.columns, rows)


def drop_duplicates(table: Table, *, subset: list[str] | None = None) -> Table:
    """Remove duplicate rows, keeping the first occurrence."""
    columns = subset if subset is not None else table.columns
    for name in columns:
        table.column(name)  # validate

    seen: set[tuple] = set()
    rows = []
    for row in table:
        key = tuple(_hashable(row[name]) for name in columns)
        if key in seen:
            continue
        seen.add(key)
        rows.append(dict(row))
    return Table(table.columns, rows)


def _hashable(value):
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, dict):
        return tuple(sorted(value.items()))
    return value
