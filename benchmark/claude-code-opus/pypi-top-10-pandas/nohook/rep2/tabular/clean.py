"""Data-cleaning transformations. Each function returns a new Table."""

from __future__ import annotations

import re
import statistics
from typing import Any, Callable, Literal, Mapping, Sequence

from .table import Table

FillStrategy = Literal["mean", "median", "mode", "ffill", "bfill"]


def normalize_column_names(table: Table) -> Table:
    """Convert column names to snake_case, e.g. ``"First Name"`` -> ``"first_name"``.

    Names that collide after normalization get a numeric suffix.
    """
    mapping: dict[str, str] = {}
    seen: set[str] = set()
    for col in table.columns:
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", col.strip())
        name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower() or "column"
        base, i = name, 2
        while name in seen:
            name, i = f"{base}_{i}", i + 1
        seen.add(name)
        mapping[col] = name
    return table.rename(mapping)


def strip_whitespace(table: Table, *, collapse: bool = False) -> Table:
    """Strip leading/trailing whitespace from string cells.

    With ``collapse``, internal runs of whitespace become a single space.
    Cells that become empty are set to ``None``.
    """

    def clean(v: Any) -> Any:
        if not isinstance(v, str):
            return v
        v = re.sub(r"\s+", " ", v).strip() if collapse else v.strip()
        return v or None

    return _map_cells(table, table.columns, clean)


def drop_duplicates(table: Table, subset: Sequence[str] | None = None) -> Table:
    """Remove repeated rows, keeping the first occurrence.

    If ``subset`` is given, only those columns are compared.
    """
    keys = list(subset) if subset is not None else table.columns
    table.select(keys)  # validate column names
    seen: set[tuple] = set()
    kept = []
    for row in table:
        key = tuple(_hashable(row[k]) for k in keys)
        if key not in seen:
            seen.add(key)
            kept.append(row)
    return Table(table.columns, kept)


def drop_missing(
    table: Table,
    subset: Sequence[str] | None = None,
    how: Literal["any", "all"] = "any",
) -> Table:
    """Drop rows with missing values in ``subset`` (default: all columns).

    ``how="any"`` drops a row if any of those values is missing;
    ``how="all"`` only if all of them are.
    """
    keys = list(subset) if subset is not None else table.columns
    table.select(keys)
    test = any if how == "any" else all
    return table.filter(lambda r: not test(r[k] is None for k in keys))


def drop_columns(table: Table, columns: Sequence[str]) -> Table:
    table.select(columns)
    return table.select([c for c in table.columns if c not in set(columns)])


def fill_missing(
    table: Table,
    value: Any = None,
    *,
    strategy: FillStrategy | None = None,
    columns: Sequence[str] | None = None,
) -> Table:
    """Replace missing values.

    Pass either a constant ``value`` (or a ``{column: value}`` mapping), or a
    ``strategy``: ``"mean"``/``"median"`` (numeric columns only), ``"mode"``,
    ``"ffill"`` (carry the previous value forward) or ``"bfill"``.
    """
    if (value is None) == (strategy is None):
        raise ValueError("pass exactly one of 'value' or 'strategy'")
    cols = list(columns) if columns is not None else table.columns
    if isinstance(value, Mapping):
        cols = [c for c in cols if c in value]
    table.select(cols)

    result = table
    for col in cols:
        values = result.column(col)
        if strategy in ("ffill", "bfill"):
            filled = _directional_fill(values, reverse=strategy == "bfill")
        else:
            fill = value[col] if isinstance(value, Mapping) else value
            if strategy is not None:
                fill = _statistic(col, values, strategy)
            filled = [fill if v is None else v for v in values]
        result = result.with_column(col, filled)
    return result


def cast_column(table: Table, column: str, converter: Callable[[Any], Any], *, errors: Literal["raise", "null"] = "raise") -> Table:
    """Apply ``converter`` to every non-missing value in ``column``.

    With ``errors="null"``, values that fail to convert become ``None``.
    """

    def convert(v: Any) -> Any:
        try:
            return converter(v)
        except (ValueError, TypeError):
            if errors == "raise":
                raise
            return None

    return _map_cells(table, [column], convert)


def replace_values(table: Table, mapping: Mapping[Any, Any], columns: Sequence[str] | None = None) -> Table:
    """Replace exact cell values, e.g. ``{"M": "male", "F": "female"}``."""
    return _map_cells(
        table,
        columns if columns is not None else table.columns,
        lambda v: mapping.get(v, v) if _is_hashable(v) else v,
    )


def remove_outliers(table: Table, column: str, *, factor: float = 1.5) -> Table:
    """Drop rows whose ``column`` value lies outside the Tukey fences
    ``[Q1 - factor*IQR, Q3 + factor*IQR]``. Rows with missing values are kept.
    """
    values = [v for v in table.column(column) if v is not None]
    if len(values) < 4:
        return table
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    low, high = q1 - factor * (q3 - q1), q3 + factor * (q3 - q1)
    return table.filter(lambda r: r[column] is None or low <= r[column] <= high)


def _map_cells(table: Table, columns: Sequence[str], fn: Callable[[Any], Any]) -> Table:
    result = table
    for col in columns:
        result = result.with_column(col, [None if v is None else fn(v) for v in result.column(col)])
    return result


def _directional_fill(values: list[Any], reverse: bool) -> list[Any]:
    seq = values[::-1] if reverse else values
    out, last = [], None
    for v in seq:
        last = v if v is not None else last
        out.append(last)
    return out[::-1] if reverse else out


def _statistic(column: str, values: list[Any], strategy: str) -> Any:
    present = [v for v in values if v is not None]
    if not present:
        return None
    if strategy == "mode":
        return statistics.mode(present)
    if not all(_is_number(v) for v in present):
        raise TypeError(f"strategy {strategy!r} requires a numeric column; {column!r} is not")
    if strategy == "mean":
        return statistics.fmean(present)
    if strategy == "median":
        return statistics.median(present)
    raise ValueError(f"unknown strategy: {strategy!r}")


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_hashable(v: Any) -> bool:
    try:
        hash(v)
    except TypeError:
        return False
    return True


def _hashable(v: Any) -> Any:
    return v if _is_hashable(v) else repr(v)
