"""Data cleaning operations for :class:`~csvlab.table.Table`."""

from __future__ import annotations

import re
import statistics
from typing import Any, Callable, Iterable

from .table import Table

Scalar = Any


def _is_blank(value: Scalar) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def strip_whitespace(table: Table, columns: Iterable[str] | None = None) -> Table:
    """Trim surrounding whitespace from string cells."""

    targets = set(columns) if columns is not None else set(table.columns)

    def clean(value: Scalar) -> Scalar:
        return value.strip() if isinstance(value, str) else value

    result = table
    for name in table.columns:
        if name in targets:
            result = result.map_column(name, clean)
    return result


def drop_empty_rows(table: Table) -> Table:
    rows = [row for row in table.to_rows() if not all(_is_blank(v) for v in row)]
    return Table(table.columns, rows)


def drop_empty_columns(table: Table) -> Table:
    keep = [
        name
        for name in table.columns
        if any(not _is_blank(v) for v in table.column(name))
    ]
    return table.select(*keep)


def drop_duplicates(
    table: Table,
    subset: Iterable[str] | None = None,
    *,
    keep: str = "first",
) -> Table:
    """Remove duplicate rows, optionally comparing only ``subset`` columns."""

    if keep not in {"first", "last", "none"}:
        raise ValueError("keep must be 'first', 'last' or 'none'")
    columns = list(subset) if subset is not None else list(table.columns)
    positions = [table.index(name) for name in columns]

    def signature(row: list[Any]) -> tuple:
        return tuple(row[p] for p in positions)

    rows = table.to_rows()
    if keep == "first":
        seen: set = set()
        kept = []
        for row in rows:
            sig = signature(row)
            if sig not in seen:
                seen.add(sig)
                kept.append(row)
        return Table(table.columns, kept)
    if keep == "last":
        seen = set()
        kept = []
        for row in reversed(rows):
            sig = signature(row)
            if sig not in seen:
                seen.add(sig)
                kept.append(row)
        return Table(table.columns, list(reversed(kept)))

    counts: dict[tuple, int] = {}
    for row in rows:
        sig = signature(row)
        counts[sig] = counts.get(sig, 0) + 1
    return Table(table.columns, [row for row in rows if counts[signature(row)] == 1])


def drop_missing(
    table: Table,
    subset: Iterable[str] | None = None,
    *,
    how: str = "any",
    thresh: int | None = None,
) -> Table:
    """Drop rows containing missing values.

    ``how='any'`` removes rows with any missing value, ``how='all'`` removes
    rows where every selected value is missing. ``thresh`` keeps rows with at
    least that many non-missing selected values.
    """

    if how not in {"any", "all"}:
        raise ValueError("how must be 'any' or 'all'")
    columns = list(subset) if subset is not None else list(table.columns)
    positions = [table.index(name) for name in columns]
    if thresh is None:
        if how == "any":
            keep = lambda row: all(not _is_blank(row[p]) for p in positions)
        else:
            keep = lambda row: not all(_is_blank(row[p]) for p in positions)
    else:
        keep = lambda row: sum(
            not _is_blank(row[p]) for p in positions
        ) >= thresh
    return Table(table.columns, [row for row in table.to_rows() if keep(row)])


def fill_missing(
    table: Table,
    value: Scalar = None,
    *,
    strategy: str = "value",
    columns: Iterable[str] | None = None,
) -> Table:
    """Replace missing values.

    Strategies: ``value`` (a fixed value), ``mean``, ``median``, ``mode``
    (numeric columns), ``ffill`` or ``bfill`` (last/next valid value).
    """

    targets = list(columns) if columns is not None else list(table.columns)
    valid = {"value", "mean", "median", "mode", "ffill", "bfill"}
    if strategy not in valid:
        raise ValueError(f"strategy must be one of {sorted(valid)}")

    result = table
    for name in targets:
        values = table.column(name)
        if strategy == "value":
            replacement = value
            result = result.map_column(
                name, lambda v, r=replacement: r if _is_blank(v) else v
            )
            continue
        if strategy in {"mean", "median", "mode"}:
            present = [v for v in values if not _is_blank(v)]
            if not present:
                continue
            if strategy == "mean":
                numeric = [v for v in present if isinstance(v, (int, float))]
                if not numeric:
                    continue
                replacement = statistics.mean(numeric)
            elif strategy == "median":
                numeric = [v for v in present if isinstance(v, (int, float))]
                if not numeric:
                    continue
                replacement = statistics.median(numeric)
            else:
                replacement = statistics.mode(present)
                if isinstance(replacement, (int, float)) and not isinstance(
                    replacement, bool
                ):
                    pass
            result = result.map_column(
                name, lambda v, r=replacement: r if _is_blank(v) else v
            )
            continue

        filled: list[Any] = []
        ordered = values if strategy == "ffill" else list(reversed(values))
        last: Scalar = None
        for v in ordered:
            if not _is_blank(v):
                last = v
            filled.append(last if _is_blank(v) else v)
        if strategy == "bfill":
            filled.reverse()
        positions = [table.index(name)]
        rows = result.to_rows()
        for row, replacement in zip(rows, filled):
            row[positions[0]] = replacement
        result = Table(result.columns, rows)
    return result


def rename_columns(table: Table, mapping: dict[str, str]) -> Table:
    return table.rename(mapping)


def normalize_column_names(table: Table) -> Table:
    """Convert headers to lowercase snake_case."""

    def norm(name: str) -> str:
        cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip()).strip("_")
        return cleaned.lower() or "column"

    mapping: dict[str, str] = {}
    used: set[str] = set()
    for name in table.columns:
        candidate = norm(name)
        unique = candidate
        counter = 1
        while unique in used:
            counter += 1
            unique = f"{candidate}_{counter}"
        used.add(unique)
        mapping[name] = unique
    return table.rename(mapping)


_COERCIONS: dict[str, Callable[[Any], Any]] = {
    "int": lambda v: int(float(v)) if isinstance(v, str) else int(v),
    "float": float,
    "str": str,
    "bool": lambda v: (
        v.strip().lower() in {"true", "yes", "1"}
        if isinstance(v, str)
        else bool(v)
    ),
}


def coerce_types(
    table: Table,
    types: dict[str, str | Callable[[Any], Any]],
) -> Table:
    """Coerce columns to the requested type, preserving missing values."""

    result = table
    for name, target in types.items():
        table.index(name)
        if isinstance(target, str):
            if target not in _COERCIONS:
                raise ValueError(f"unknown target type: {target!r}")
            func = _COERCIONS[target]
        else:
            func = target

        def convert(value: Scalar, f: Callable[[Any], Any] = func) -> Scalar:
            if _is_blank(value):
                return None
            return f(value)

        result = result.map_column(name, convert)
    return result


def replace_values(
    table: Table,
    replacements: dict[Any, Any],
    columns: Iterable[str] | None = None,
) -> Table:
    targets = set(columns) if columns is not None else set(table.columns)
    result = table
    for name in table.columns:
        if name in targets:
            result = result.map_column(
                name, lambda v, r=replacements: r.get(v, v)
            )
    return result
