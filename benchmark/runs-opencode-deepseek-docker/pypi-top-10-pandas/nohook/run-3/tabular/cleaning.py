"""Functions that clean and normalise tabular data.

Every function accepts a :class:`~tabular.table.Table` and returns a new
``Table``; the input is never modified.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from .table import Table

DEFAULT_MISSING = frozenset(
    {"", "na", "n/a", "null", "none", "nan", "nil", "missing", "-"}
)

_DEFAULT_TOKENS = frozenset(token.lower() for token in DEFAULT_MISSING)


def normalize_missing(missing: Iterable[str]) -> frozenset[str]:
    """Return a lower-cased, stripped set of missing-value tokens."""
    return frozenset(str(token).strip().lower() for token in missing)


def looks_missing(value: Any, tokens: frozenset[str]) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in tokens
    return False


def is_missing(value: Any, missing: Iterable[str] = DEFAULT_MISSING) -> bool:
    """Return whether ``value`` counts as missing."""
    return looks_missing(value, normalize_missing(missing))


def _column_indexes(table: Table, columns: Sequence[str] | None) -> list[int]:
    if columns is None:
        return list(range(len(table.headers)))
    return [table._index(column) for column in columns]


def strip_whitespace(table: Table) -> Table:
    """Trim surrounding whitespace from headers and string values."""
    headers = [header.strip() for header in table.headers]
    rows = [
        [value.strip() if isinstance(value, str) else value for value in row]
        for row in table.rows
    ]
    return Table(headers, rows)


def standardize_headers(
    table: Table, *, lower: bool = True, separator: str = "_"
) -> Table:
    """Normalise header names into ``snake_case`` style identifiers."""
    headers = []
    for header in table.headers:
        cleaned = header.strip().replace(" ", separator).replace("-", separator)
        if lower:
            cleaned = cleaned.lower()
        headers.append(cleaned)
    return Table(headers, table.rows)


def replace_missing(
    table: Table, missing: Iterable[str] = DEFAULT_MISSING
) -> Table:
    """Replace missing tokens with ``None``."""
    tokens = normalize_missing(missing)
    rows = [
        [None if looks_missing(value, tokens) else value for value in row]
        for row in table.rows
    ]
    return Table(table.headers, rows)


def drop_empty_rows(table: Table) -> Table:
    """Drop rows whose every value is missing."""
    rows = [
        row
        for row in table.rows
        if any(not looks_missing(value, _DEFAULT_TOKENS) for value in row)
    ]
    return Table(table.headers, rows)


def drop_empty_columns(table: Table) -> Table:
    """Drop columns whose every value is missing."""
    if not table.rows:
        return table.copy()
    keep = [
        index
        for index in range(len(table.headers))
        if any(
            not looks_missing(row[index], _DEFAULT_TOKENS) for row in table.rows
        )
    ]
    headers = [table.headers[index] for index in keep]
    rows = [[row[index] for index in keep] for row in table.rows]
    return Table(headers, rows)


def drop_missing(
    table: Table,
    *,
    columns: Sequence[str] | None = None,
    how: str = "any",
    missing: Iterable[str] = DEFAULT_MISSING,
) -> Table:
    """Drop rows containing missing values in the selected columns.

    ``how`` may be ``"any"`` (drop when at least one selected value is missing)
    or ``"all"`` (drop only when every selected value is missing).
    """
    if how not in {"any", "all"}:
        raise ValueError("how must be 'any' or 'all'")
    indexes = _column_indexes(table, columns)
    tokens = normalize_missing(missing)

    rows = []
    for row in table.rows:
        flags = [looks_missing(row[index], tokens) for index in indexes]
        discard = any(flags) if how == "any" else all(flags)
        if not discard:
            rows.append(row)
    return Table(table.headers, rows)


def fill_missing(
    table: Table,
    value: Any = None,
    *,
    columns: Sequence[str] | None = None,
    missing: Iterable[str] = DEFAULT_MISSING,
) -> Table:
    """Replace missing values in the selected columns with ``value``."""
    indexes = set(_column_indexes(table, columns))
    tokens = normalize_missing(missing)
    rows = [
        [
            value if index in indexes and looks_missing(cell, tokens) else cell
            for index, cell in enumerate(row)
        ]
        for row in table.rows
    ]
    return Table(table.headers, rows)


def drop_duplicates(
    table: Table, *, columns: Sequence[str] | None = None
) -> Table:
    """Drop duplicate rows, keeping the first occurrence."""
    indexes = _column_indexes(table, columns)
    seen: set[tuple[Any, ...]] = set()
    rows = []
    for row in table.rows:
        signature = tuple(row[index] for index in indexes)
        if signature not in seen:
            seen.add(signature)
            rows.append(row)
    return Table(table.headers, rows)


def _coerce_number(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text == "":
        return value
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return value


def coerce_numeric(
    table: Table, *, columns: Sequence[str] | None = None
) -> Table:
    """Convert numeric-looking strings into ``int`` or ``float``.

    Non-numeric values are left untouched.
    """
    indexes = set(_column_indexes(table, columns))
    rows = [
        [
            _coerce_number(cell) if index in indexes else cell
            for index, cell in enumerate(row)
        ]
        for row in table.rows
    ]
    return Table(table.headers, rows)
