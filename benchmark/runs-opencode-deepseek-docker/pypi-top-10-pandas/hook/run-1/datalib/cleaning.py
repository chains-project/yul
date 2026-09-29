"""Cleaning and type-coercion operations.

Every function returns a **new** :class:`~datalib.table.Table`; the input table
is never mutated.  This makes the operations easy to chain::

    from datalib import load_csv, cleaning

    table = cleaning.clean(load_csv("raw.csv"))
"""

from __future__ import annotations

import datetime as _dt
import statistics
from typing import Any, Callable, Iterable, Mapping, Sequence

from .exceptions import DataLibError, SchemaError
from .table import Table

# Tokens that are treated as "missing" when parsing a CSV.
NULL_TOKENS = frozenset(
    {"", "na", "n/a", "n.a.", "null", "none", "nan", "nil", "-", "--", "?"}
)

_TRUE_TOKENS = frozenset({"true", "t", "yes", "y", "1"})
_FALSE_TOKENS = frozenset({"false", "f", "no", "n", "0"})

_NUMBER_TYPES = ("int", "float")
_DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S")


# ----------------------------------------------------------------------
# Scalar parsers / casters
# ----------------------------------------------------------------------
def is_missing(value: Any) -> bool:
    """Return ``True`` when ``value`` is ``None`` or a known null token."""
    return value is None or (
        isinstance(value, str) and value.strip().lower() in NULL_TOKENS
    )


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_number(value: Any) -> int | float | None:
    """Parse ``value`` as an ``int`` or ``float``, or return ``None``."""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip().replace(",", "")
    if text == "" or text.lower() in NULL_TOKENS:
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return None


def parse_bool(value: Any) -> bool | None:
    """Parse ``value`` as a boolean, or return ``None`` when it is not one."""
    if value is None or isinstance(value, bool):
        return value
    token = str(value).strip().lower()
    if token in _TRUE_TOKENS:
        return True
    if token in _FALSE_TOKENS:
        return False
    return None


def parse_date(value: Any) -> _dt.date | None:
    """Parse ``value`` as a :class:`datetime.date`, or return ``None``."""
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return _dt.date.fromisoformat(text)
    except ValueError:
        pass
    for fmt in _DATE_FORMATS:
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


_CASTERS: dict[str, Callable[[Any], Any]] = {
    "str": lambda v: None if v is None else str(v),
    "int": parse_number,
    "float": parse_number,
    "number": parse_number,
    "bool": parse_bool,
    "date": parse_date,
}


def _coerce_value(value: Any, type_name: str) -> Any:
    if type_name not in _CASTERS:
        raise SchemaError(f"unknown target type: {type_name!r}")
    if is_missing(value):
        return None
    result = _CASTERS[type_name](value)
    if result is None:
        raise SchemaError(f"cannot cast {value!r} to {type_name}")
    if type_name == "int" and isinstance(result, float) and not result.is_integer():
        raise SchemaError(f"cannot cast {value!r} to int losslessly")
    if type_name == "int":
        return int(result)
    if type_name == "float":
        return float(result)
    return result


# ----------------------------------------------------------------------
# Type inference
# ----------------------------------------------------------------------
def infer_column_type(values: Sequence[Any]) -> str:
    """Best-effort type name for a column of values.

    Returns one of ``"int"``, ``"float"``, ``"bool"``, ``"date"`` or ``"str"``.
    """
    non_null = [v for v in values if not is_missing(v)]
    if not non_null:
        return "str"

    if all(isinstance(v, bool) for v in non_null):
        return "bool"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in non_null):
        return "int"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in non_null):
        return "float"

    # Try parsers only for string-ish input; never misclassify arbitrary objects.
    if all(isinstance(v, str) for v in non_null):
        numbers = [parse_number(v) for v in non_null]
        if all(n is not None for n in numbers):
            if all(float(n).is_integer() for n in numbers):
                return "int"
            return "float"
        if all(parse_bool(v) is not None for v in non_null):
            return "bool"
        if all(parse_date(v) is not None for v in non_null):
            return "date"
    return "str"


# ----------------------------------------------------------------------
# Table-level operations
# ----------------------------------------------------------------------
def _resolve(table: Table, columns: Iterable[str] | None) -> list[str]:
    if columns is None:
        return list(table.columns)
    resolved = list(columns)
    for name in resolved:
        table._require(name)
    return resolved


def strip_whitespace(
    table: Table, columns: Iterable[str] | None = None
) -> Table:
    """Trim surrounding whitespace from string values."""
    target = set(_resolve(table, columns))

    def clean_row(row):
        return {
            key: (value.strip() if key in target and isinstance(value, str) else value)
            for key, value in row.items()
        }

    return Table(table.columns, [clean_row(row) for row in table.rows])


def drop_missing(
    table: Table,
    how: str = "any",
    subset: Iterable[str] | None = None,
) -> Table:
    """Remove rows containing missing values.

    ``how="any"`` drops a row if any inspected value is missing; ``how="all"``
    drops it only when every inspected value is missing.
    """
    if how not in ("any", "all"):
        raise DataLibError("how must be 'any' or 'all'")
    cols = _resolve(table, subset)

    def keep(row):
        flags = [is_missing(row[c]) for c in cols]
        return not (any(flags) if how == "any" else all(flags))

    return Table(table.columns, [row for row in table.rows if keep(row)])


def drop_empty_rows(table: Table, how: str = "any", subset=None) -> Table:
    """Alias of :func:`drop_missing` for rows that are blank."""
    return drop_missing(table, how=how, subset=subset)


def drop_duplicates(
    table: Table,
    subset: Iterable[str] | None = None,
    keep: str | bool = "first",
) -> Table:
    """Remove duplicate rows.

    ``keep`` is ``"first"``, ``"last"`` or ``False`` (drop all duplicates).
    """
    if keep not in ("first", "last", False):
        raise DataLibError("keep must be 'first', 'last' or False")
    cols = _resolve(table, subset)

    buckets: dict[tuple, list[int]] = {}
    for index, row in enumerate(table.rows):
        key = tuple(row[c] for c in cols)
        buckets.setdefault(key, []).append(index)

    keep_indices: set[int] = set()
    for indices in buckets.values():
        if len(indices) == 1:
            keep_indices.add(indices[0])
        elif keep == "first":
            keep_indices.add(indices[0])
        elif keep == "last":
            keep_indices.add(indices[-1])
        # keep is False -> drop every row in the duplicate group

    return Table(
        table.columns,
        [row for i, row in enumerate(table.rows) if i in keep_indices],
    )


def fill_missing(
    table: Table,
    value: Any = None,
    columns: Iterable[str] | None = None,
    strategy: str = "value",
) -> Table:
    """Replace missing values.

    ``strategy`` is one of ``"value"``, ``"mean"``, ``"median"``, ``"mode"``,
    ``"ffill"`` (forward fill) or ``"bfill"`` (backward fill).  For the
    ``ffill``/``bfill`` strategies ``columns`` defaults to all columns.
    """
    target = _resolve(table, columns)

    if strategy not in ("value", "mean", "median", "mode", "ffill", "bfill"):
        raise DataLibError(f"unknown fill strategy: {strategy!r}")

    fillers: dict[str, Any] = {}
    if strategy in ("mean", "median", "mode"):
        for name in target:
            values = [v for v in table.column(name) if not is_missing(v)]
            if strategy in ("mean", "median"):
                numbers = [v for v in values if _is_number(v)]
                if not numbers:
                    fillers[name] = value
                elif strategy == "mean":
                    fillers[name] = statistics.fmean(numbers)
                else:
                    fillers[name] = statistics.median(numbers)
            elif values:
                fillers[name] = statistics.mode(values)
            else:
                fillers[name] = value

    rows = [dict(row) for row in table.rows]

    if strategy == "ffill":
        last: dict[str, Any] = {}
        for row in rows:
            for name in target:
                if is_missing(row[name]):
                    row[name] = last.get(name)
                else:
                    last[name] = row[name]
        return Table(table.columns, rows)

    if strategy == "bfill":
        nxt: dict[str, Any] = {}
        for row in reversed(rows):
            for name in target:
                if is_missing(row[name]):
                    row[name] = nxt.get(name)
                else:
                    nxt[name] = row[name]
        return Table(table.columns, rows)

    for row in rows:
        for name in target:
            if is_missing(row[name]):
                row[name] = fillers[name] if strategy != "value" else value

    return Table(table.columns, rows)


def replace_values(
    table: Table,
    replacements: Mapping[Any, Any],
    columns: Iterable[str] | None = None,
) -> Table:
    """Replace exact values according to ``replacements``."""
    target = set(_resolve(table, columns))

    def replace_row(row):
        return {
            key: (replacements.get(val, val) if key in target else val)
            for key, val in row.items()
        }

    return Table(table.columns, [replace_row(row) for row in table.rows])


def rename_columns(table: Table, mapping: Mapping[str, str]) -> Table:
    """Return a copy of ``table`` with columns renamed."""
    return table.rename(mapping)


def drop_columns(table: Table, columns: Iterable[str]) -> Table:
    """Return a copy of ``table`` without ``columns``."""
    return table.drop_column(*list(columns))


def coerce_types(
    table: Table,
    schema: Mapping[str, str] | None = None,
    infer: bool = False,
) -> Table:
    """Cast columns to declared (and/or inferred) types.

    Parameters
    ----------
    schema:
        Optional mapping of column name to one of ``"str"``, ``"int"``,
        ``"float"``, ``"number"``, ``"bool"`` or ``"date"``.
    infer:
        When true, every column not present in ``schema`` has its type
        inferred and applied.
    """
    schema = dict(schema or {})
    for name in schema:
        table._require(name)

    if infer:
        for name in table.columns:
            if name not in schema:
                schema.setdefault(name, infer_column_type(table.column(name)))

    rows = [dict(row) for row in table.rows]
    for name, type_name in schema.items():
        for row in rows:
            row[name] = _coerce_value(row[name], type_name)

    return Table(table.columns, rows)


def clean(
    table: Table,
    *,
    strip: bool = True,
    drop_empty: bool = True,
    how: str = "any",
    drop_dupes: bool = False,
    subset: Iterable[str] | None = None,
    fill: Any = None,
    fill_strategy: str | None = None,
    fill_columns: Iterable[str] | None = None,
    schema: Mapping[str, str] | None = None,
    infer: bool = False,
) -> Table:
    """Run a conventional cleaning pipeline in a single call.

    The steps run in this order: strip whitespace, drop empty rows, drop
    duplicates, fill missing values, coerce types.  ``subset`` limits the
    empty-row and duplicate checks; ``fill_columns`` limits filling (all
    columns by default).
    """
    result = table
    if strip:
        result = strip_whitespace(result)
    if drop_empty:
        result = drop_missing(result, how=how, subset=subset)
    if drop_dupes:
        result = drop_duplicates(result, subset=subset)
    if fill_strategy is not None:
        result = fill_missing(
            result, value=fill, columns=fill_columns, strategy=fill_strategy
        )
    if schema or infer:
        result = coerce_types(result, schema=schema, infer=infer)
    return result
