"""Cleaning and transformation utilities for :class:`~csvlib.table.Table`."""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Optional

from ._utils import is_missing, resolve_columns, uniquify
from .table import Table

_BOOL_TRUE = frozenset({"true", "yes"})
_BOOL_FALSE = frozenset({"false", "no"})
_INT_RE = re.compile(r"[+-]?(0|[1-9]\d*)\Z")
_DIGITS_ONLY = re.compile(r"[+-]?\d+\Z")


def _map_column(table: Table, columns: Iterable[str], func: Callable[[Any], Any]) -> Table:
    columns = set(columns)
    return table.with_rows(
        [
            {key: (func(value) if key in columns else value) for key, value in row.items()}
            for row in table
        ]
    )


def strip_whitespace(table: Table, columns: Optional[Any] = None) -> Table:
    """Strip leading/trailing whitespace from string cells."""
    selected = set(resolve_columns(table, columns))

    def clean(value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    return _map_column(table, selected, clean)


def replace_values(
    table: Table,
    mapping: Mapping[Any, Any],
    columns: Optional[Any] = None,
) -> Table:
    """Replace cells matching keys in *mapping* with the corresponding values."""
    selected = set(resolve_columns(table, columns))

    def clean(value: Any) -> Any:
        return mapping.get(value, value)

    return _map_column(table, selected, clean)


def fill_missing(table: Table, value: Any, columns: Optional[Any] = None) -> Table:
    """Replace missing cells with *value*."""
    selected = set(resolve_columns(table, columns))

    def clean(current: Any) -> Any:
        return value if is_missing(current) else current

    return _map_column(table, selected, clean)


def drop_empty_rows(table: Table) -> Table:
    """Drop rows whose every cell is missing."""
    return table.with_rows(
        [row for row in table if not all(is_missing(v) for v in row.values())]
    )


def drop_empty_columns(table: Table) -> Table:
    """Drop columns whose every cell is missing."""
    keep = [
        column
        for column in table.columns
        if not all(is_missing(row[column]) for row in table)
    ]
    return select_columns(table, keep)


def drop_missing_rows(
    table: Table,
    columns: Optional[Any] = None,
    how: str = "any",
) -> Table:
    """Drop rows containing missing values.

    *how* may be ``"any"`` (drop if any selected cell is missing) or ``"all"``
    (drop only if every selected cell is missing).
    """
    if how not in ("any", "all"):
        raise ValueError("how must be 'any' or 'all'")
    selected = resolve_columns(table, columns)
    reducer = any if how == "any" else all
    return table.with_rows(
        [row for row in table if not reducer(is_missing(row[c]) for c in selected)]
    )


def drop_missing_columns(table: Table, threshold: float = 1.0) -> Table:
    """Drop columns whose missing fraction is at least *threshold*."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    total = table.num_rows
    keep = []
    for column in table.columns:
        missing = sum(1 for value in table.column(column) if is_missing(value))
        fraction = missing / total if total else 0.0
        if fraction < threshold:
            keep.append(column)
    return select_columns(table, keep)


def drop_duplicates(table: Table, subset: Optional[Any] = None) -> Table:
    """Drop duplicate rows, optionally considering only *subset* of columns."""
    selected = resolve_columns(table, subset)
    seen: set[tuple[Any, ...]] = set()
    rows = []
    for row in table:
        key = tuple(_hashable(row[c]) for c in selected)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return table.with_rows(rows)


def _hashable(value: Any) -> Any:
    try:
        hash(value)
    except TypeError:
        return repr(value)
    return value


def filter_rows(table: Table, predicate: Callable[[dict[str, Any]], bool]) -> Table:
    """Keep rows for which ``predicate(row)`` is truthy."""
    return table.filter(predicate)


def select_columns(table: Table, columns: Iterable[str]) -> Table:
    """Return a table containing only *columns*, in order."""
    columns = list(columns)
    unknown = [c for c in columns if c not in table.columns]
    if unknown:
        raise KeyError(f"Unknown column(s): {', '.join(map(repr, unknown))}")
    return Table(columns, [[row[c] for c in columns] for row in table])


def rename_columns(table: Table, mapping: Mapping[str, str]) -> Table:
    """Rename columns according to *mapping*."""
    return table.rename(mapping)


def normalize_columns(table: Table, *, case: str = "snake") -> Table:
    """Normalize column names.

    *case* is either ``"snake"`` (``"First Name" -> "first_name"``) or
    ``"lower"`` (just lowercase and trim).
    """
    if case not in ("snake", "lower"):
        raise ValueError("case must be 'snake' or 'lower'")
    if case == "lower":
        new_names = uniquify([c.strip().lower() or "column" for c in table.columns])
    else:
        new_names = uniquify([_to_snake(c) for c in table.columns])
    return Table(new_names, table.to_rows())


def _to_snake(name: str) -> str:
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name.strip())
    name = re.sub(r"[^\w]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_").lower()
    return name or "column"


def convert_column(
    table: Table,
    column: str,
    converter: Callable[[Any], Any],
    *,
    errors: str = "raise",
) -> Table:
    """Apply *converter* to every non-missing cell of *column*.

    *errors* may be ``"raise"``, ``"ignore"`` (leave the cell unchanged) or
    ``"coerce"`` (replace with ``None``).
    """
    if errors not in ("raise", "ignore", "coerce"):
        raise ValueError("errors must be 'raise', 'ignore' or 'coerce'")
    resolve_columns(table, [column])

    def clean(value: Any) -> Any:
        if is_missing(value):
            return None
        try:
            return converter(value)
        except (TypeError, ValueError):
            if errors == "raise":
                raise
            return None if errors == "coerce" else value

    return _map_column(table, {column}, clean)


def coerce_types(table: Table, columns: Optional[Any] = None) -> Table:
    """Infer and apply integer/float/bool types column by column.

    A column is converted only when *every* non-missing value parses cleanly
    as the same type.  Missing cells remain ``None``.
    """
    selected = resolve_columns(table, columns)
    result = table
    for column in selected:
        converted = _infer_series(result.column(column))
        if converted is not None:
            result = _map_column(result, {column}, _make_replacer(converted))
    return result


def _make_replacer(values: list[Any]) -> Callable[[Any], Any]:
    iterator = iter(values)

    def replace(_: Any) -> Any:
        return next(iterator)

    return replace


def _infer_series(values: list[Any]) -> Optional[list[Any]]:
    for parser in (_parse_int, _parse_float, _parse_bool):
        try:
            return [
                None if is_missing(value) else parser(value)  # type: ignore[arg-type]
                for value in values
            ]
        except (TypeError, ValueError):
            continue
    return None


def _parse_int(value: Any) -> int:
    if isinstance(value, bool):
        raise TypeError("bool is not int")
    text = str(value).strip()
    if not _INT_RE.match(text):
        raise ValueError(f"not an integer: {value!r}")
    return int(text)


def _parse_float(value: Any) -> float:
    if isinstance(value, bool):
        raise TypeError("bool is not float")
    text = str(value).strip()
    if "_" in text:
        raise ValueError(f"not a float: {value!r}")
    if _DIGITS_ONLY.match(text) and not _INT_RE.match(text):
        raise ValueError(f"not a float: {value!r}")
    parsed = float(text)
    if not math.isfinite(parsed):
        raise ValueError(f"not a finite number: {value!r}")
    return parsed


def _parse_bool(value: Any) -> bool:
    text = str(value).strip().lower()
    if text in _BOOL_TRUE:
        return True
    if text in _BOOL_FALSE:
        return False
    raise ValueError(f"not a boolean: {value!r}")
