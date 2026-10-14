"""Reading and writing CSV files, with type inference."""

from __future__ import annotations

import csv
import datetime as dt
import os
from typing import Any, Callable, Iterable, Sequence

from .table import Table

DEFAULT_NA_VALUES = frozenset({"", "na", "n/a", "nan", "null", "none", "-", "?"})
_TRUE = {"true", "yes", "y", "t"}
_FALSE = {"false", "no", "n", "f"}

PathLike = str | os.PathLike


def _parse_bool(text: str) -> bool:
    lowered = text.lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ValueError(text)


def _parse_int(text: str) -> int:
    _reject_leading_zero(text)
    return int(text.replace(",", "") if _is_grouped_number(text) else text)


def _parse_float(text: str) -> float:
    _reject_leading_zero(text)
    return float(text.replace(",", "") if _is_grouped_number(text) else text)


def _reject_leading_zero(text: str) -> None:
    """Keep identifiers like ZIP codes ("02134") as text instead of numbers."""
    digits = text.lstrip("+-").split(".", 1)[0]
    if len(digits) > 1 and digits.startswith("0") and digits.isdigit():
        raise ValueError(text)


def _is_grouped_number(text: str) -> bool:
    """True for thousands-separated numbers such as ``1,234,567.89``."""
    head = text.lstrip("+-").split(".", 1)[0]
    groups = head.split(",")
    return (len(groups) > 1 and 1 <= len(groups[0]) <= 3
            and all(g.isdigit() for g in groups)
            and all(len(g) == 3 for g in groups[1:]))


# Ordered from most to least specific; the first parser that accepts every
# non-missing value in a column determines the column's type.
_PARSERS: list[tuple[str, Callable[[str], Any]]] = [
    ("int", _parse_int),
    ("float", _parse_float),
    ("bool", _parse_bool),
    ("date", dt.date.fromisoformat),
    ("datetime", dt.datetime.fromisoformat),
]


def infer_column(values: Sequence[str | None]) -> tuple[str, list[Any]]:
    """Infer a column type and return ``(type_name, converted_values)``.

    ``values`` should already have missing entries replaced with ``None``.
    Falls back to ``"str"`` when no parser accepts every value.
    """
    present = [v for v in values if v is not None]
    if not present:
        return "str", list(values)
    for name, parser in _PARSERS:
        try:
            converted = [None if v is None else parser(v) for v in values]
        except (ValueError, TypeError):
            continue
        return name, converted
    return "str", list(values)


def load_csv(
    path: PathLike,
    *,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    header: bool = True,
    na_values: Iterable[str] | None = None,
    infer_types: bool = True,
    strip: bool = True,
    usecols: Sequence[str] | None = None,
) -> Table:
    """Load a CSV file into a :class:`Table`.

    Args:
        path: File to read.
        delimiter: Field separator. Sniffed from the file when ``None``.
        encoding: Text encoding. The default transparently drops a UTF-8 BOM.
        header: Whether the first row holds column names. If ``False``,
            columns are named ``column_1``, ``column_2``, ...
        na_values: Case-insensitive strings treated as missing. Defaults to
            :data:`DEFAULT_NA_VALUES`.
        infer_types: Convert columns to int/float/bool/date/datetime when
            every non-missing value parses as that type.
        strip: Strip surrounding whitespace from every cell.
        usecols: Optional subset of columns to keep.

    Rows shorter than the header are padded with missing values; rows longer
    than the header raise ``ValueError``. Fully empty lines are skipped.
    """
    na = {s.lower() for s in (DEFAULT_NA_VALUES if na_values is None else na_values)}

    with open(path, newline="", encoding=encoding) as handle:
        if delimiter is None:
            sample = handle.read(64 * 1024)
            handle.seek(0)
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ","
        records = [r for r in csv.reader(handle, delimiter=delimiter) if any(r)]

    if not records:
        return Table({})

    if header:
        names, records = records[0], records[1:]
        names = _dedupe_names([n.strip() for n in names])
    else:
        width = max(len(r) for r in records)
        names = [f"column_{i + 1}" for i in range(width)]

    width = len(names)
    columns: list[list[str | None]] = [[] for _ in names]
    for line_no, record in enumerate(records, start=2 if header else 1):
        if len(record) > width:
            raise ValueError(
                f"{path}: row {line_no} has {len(record)} fields, expected {width}")
        record = record + [""] * (width - len(record))
        for column, cell in zip(columns, record):
            if strip:
                cell = cell.strip()
            column.append(None if cell.lower() in na else cell)

    table_data: dict[str, list[Any]] = {}
    for name, values in zip(names, columns):
        if usecols is not None and name not in usecols:
            continue
        table_data[name] = infer_column(values)[1] if infer_types else values

    if usecols is not None:
        missing = [c for c in usecols if c not in table_data]
        if missing:
            raise KeyError(f"usecols not found in {path}: {missing}")
        table_data = {c: table_data[c] for c in usecols}
    return Table(table_data)


def save_csv(table: Table, path: PathLike, *, delimiter: str = ",",
             na_rep: str = "", encoding: str = "utf-8") -> None:
    """Write ``table`` to ``path`` as CSV with a header row."""
    with open(path, "w", newline="", encoding=encoding) as handle:
        writer = csv.writer(handle, delimiter=delimiter)
        writer.writerow(table.columns)
        for row in table.rows():
            writer.writerow([na_rep if v is None else _format(v) for v in row.values()])


def _format(value: Any) -> str:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    return str(value)


def _dedupe_names(names: list[str]) -> list[str]:
    """Make header names unique and non-empty (``a, a, ''`` -> ``a, a_1, unnamed_3``)."""
    seen: dict[str, int] = {}
    result = []
    for i, name in enumerate(names):
        name = name or f"unnamed_{i + 1}"
        base = name
        while name in seen:
            seen[base] += 1
            name = f"{base}_{seen[base]}"
        seen.setdefault(name, 0)
        result.append(name)
    return result
