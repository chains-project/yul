"""Cleaning and normalization operations for :class:`~tabular.table.Table`.

Every function returns a new :class:`Table`; inputs are never mutated.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from .table import Table


def normalize_headers(table: Table, *, lower: bool = False) -> Table:
    """Trim headers and replace internal whitespace with underscores.

    Optionally lowercases names. Name collisions get a numeric suffix.
    """
    result = table.copy()
    seen: dict[str, int] = {}
    for i, raw in enumerate(result.columns):
        name = "_".join(raw.strip().split())
        if lower:
            name = name.lower()
        name = name or f"column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        result.columns[i] = name
    return result


def strip_whitespace(table: Table) -> Table:
    """Strip leading/trailing whitespace from every string cell."""
    result = table.copy()
    result.rows = [
        [cell.strip() if isinstance(cell, str) else cell for cell in row]
        for row in result.rows
    ]
    return result


def replace_values(
    table: Table,
    column: str,
    mapping: Mapping[Any, Any],
    *,
    regex: bool = False,
) -> Table:
    """Replace values in ``column`` using ``mapping``.

    With ``regex=True`` the keys are treated as regular expression patterns.
    """
    import re

    result = table.copy()
    index = result._index(column)
    if regex:
        compiled = [(re.compile(k), v) for k, v in mapping.items()]
        for row in result.rows:
            value = row[index]
            if isinstance(value, str):
                for pattern, replacement in compiled:
                    value = pattern.sub(str(replacement), value)
                row[index] = value
    else:
        for row in result.rows:
            if row[index] in mapping:
                row[index] = mapping[row[index]]
    return result


def fill_missing(
    table: Table,
    value: Any = None,
    *,
    column: str | None = None,
    method: str | None = None,
) -> Table:
    """Fill ``None`` cells.

    ``value`` may be a scalar or a callable receiving the column name. When
    ``method`` is ``"mean"``/``"median"``/``"mode"`` the fill uses that
    statistic of the column (numeric methods require numeric data).
    """
    result = table.copy()
    targets = [column] if column else list(result.columns)
    for name in targets:
        index = result._index(name)
        values = [row[index] for row in result.rows]
        if method is not None:
            present = [v for v in values if v is not None]
            if method == "mean":
                fill = sum(present) / len(present) if present else None
            elif method == "median":
                fill = _median(present)
            elif method == "mode":
                fill = max(set(present), key=present.count) if present else None
            else:
                raise ValueError(f"unknown fill method: {method!r}")
        elif callable(value):
            fill = value(name)
        else:
            fill = value
        for row in result.rows:
            if row[index] is None:
                row[index] = fill
    return result


def _median(values: Sequence[float]) -> float | None:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        return None
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def drop_missing(
    table: Table,
    *,
    subset: Sequence[str] | None = None,
    how: str = "any",
) -> Table:
    """Drop rows containing missing values.

    ``how="any"`` removes a row if any selected cell is missing; ``how="all"``
    removes it only when every selected cell is missing.
    """
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    columns = list(subset) if subset else list(table.columns)
    indices = [table._index(name) for name in columns]
    kept = []
    for row in table.rows:
        missing = [row[i] is None for i in indices]
        drop = any(missing) if how == "any" else all(missing)
        if not drop:
            kept.append(list(row))
    return Table(table.columns, kept)


def drop_empty_rows(table: Table) -> Table:
    """Drop rows where every cell is ``None`` or an empty string."""
    kept = [
        list(row)
        for row in table.rows
        if any(cell not in (None, "") for cell in row)
    ]
    return Table(table.columns, kept)


def drop_empty_columns(table: Table) -> Table:
    """Drop columns where every cell is ``None`` or an empty string."""
    keep = [
        i
        for i in range(len(table.columns))
        if any(
            row[i] not in (None, "")
            for row in table.rows
        )
    ]
    columns = [table.columns[i] for i in keep]
    rows = [[row[i] for i in keep] for row in table.rows]
    return Table(columns, rows)


def drop_duplicates(
    table: Table, *, subset: Sequence[str] | None = None
) -> Table:
    """Remove duplicate rows, keeping the first occurrence."""
    columns = list(subset) if subset else list(table.columns)
    indices = [table._index(name) for name in columns]
    seen: set[tuple[Any, ...]] = set()
    kept = []
    for row in table.rows:
        key = tuple(row[i] for i in indices)
        if key in seen:
            continue
        seen.add(key)
        kept.append(list(row))
    return Table(table.columns, kept)


def cast_column(
    table: Table, column: str, caster: Callable[[Any], Any]
) -> Table:
    """Apply ``caster`` to every cell in ``column`` (errors propagate)."""
    result = table.copy()
    index = result._index(column)
    for row in result.rows:
        if row[index] is not None:
            row[index] = caster(row[index])
    return result


def coerce_column(
    table: Table,
    column: str,
    caster: Callable[[Any], Any],
    *,
    on_error: Any = None,
) -> Table:
    """Like :func:`cast_column` but replaces failures with ``on_error``."""
    result = table.copy()
    index = result._index(column)
    for row in result.rows:
        if row[index] is None:
            continue
        try:
            row[index] = caster(row[index])
        except (TypeError, ValueError):
            row[index] = on_error
    return result


def rename_columns(table: Table, mapping: Mapping[str, str]) -> Table:
    """Return a copy with columns renamed per ``mapping``."""
    result = table.copy()
    for old, new in mapping.items():
        result.rename_column(old, new)
    return result
