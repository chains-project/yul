"""Reading and writing CSV files, with automatic type inference."""

from __future__ import annotations

import csv
import io
import os
from datetime import date, datetime
from typing import Any, Iterable, TextIO

from .table import Table

DEFAULT_NA_VALUES = frozenset({"", "na", "n/a", "nan", "null", "none", "-"})
_TRUE = {"true", "yes"}
_FALSE = {"false", "no"}


def load_csv(
    source: str | os.PathLike | TextIO,
    *,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    na_values: Iterable[str] = DEFAULT_NA_VALUES,
    infer_types: bool = True,
) -> Table:
    """Load a CSV file (path or open text stream) into a :class:`Table`.

    The first row is used as the header. If ``delimiter`` is ``None`` it is
    detected from a sample of the file. Cells matching ``na_values``
    (case-insensitive, after stripping) become ``None``. With
    ``infer_types``, each column is converted to the narrowest type that
    fits all of its non-missing values: bool, int, float, ISO date/datetime,
    otherwise str. Short rows are padded with ``None``; rows with extra
    fields raise ``ValueError``.
    """
    if isinstance(source, (str, os.PathLike)):
        with open(source, newline="", encoding=encoding) as f:
            return _read(f, delimiter, na_values, infer_types)
    return _read(source, delimiter, na_values, infer_types)


def loads_csv(text: str, **kwargs: Any) -> Table:
    """Like :func:`load_csv` but parses CSV from a string."""
    return load_csv(io.StringIO(text), **kwargs)


def save_csv(table: Table, path: str | os.PathLike, *, delimiter: str = ",", encoding: str = "utf-8") -> None:
    """Write a table to ``path``; missing values are written as empty cells."""
    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(table.columns)
        for row in table:
            writer.writerow(_format(row[c]) for c in table.columns)


def _read(f: TextIO, delimiter: str | None, na_values: Iterable[str], infer_types: bool) -> Table:
    text = f.read()
    if not text.strip():
        return Table([])
    if delimiter is None:
        delimiter = _sniff_delimiter(text)
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    header = [h.strip() for h in next(reader)]
    na = {v.strip().lower() for v in na_values}

    raw_rows: list[list[str | None]] = []
    for line_no, record in enumerate(reader, start=2):
        if not any(cell.strip() for cell in record):
            continue  # skip blank lines
        if len(record) > len(header):
            raise ValueError(f"line {line_no}: expected {len(header)} fields, got {len(record)}")
        record = record + [""] * (len(header) - len(record))
        raw_rows.append([None if cell.strip().lower() in na else cell for cell in record])

    columns: list[list[Any]] = [list(col) for col in zip(*raw_rows)] or [[] for _ in header]
    if infer_types:
        columns = [infer_column(col) for col in columns]
    return Table(header, (dict(zip(header, values)) for values in zip(*columns)))


def _sniff_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def infer_column(values: list[str | None]) -> list[Any]:
    """Convert string values to the narrowest type that fits all non-missing ones."""
    present = [v.strip() for v in values if v is not None]
    if not present:
        return list(values)
    for converter in (_to_bool, _to_int, _to_float, _to_date, _to_datetime):
        try:
            converted = [converter(v.strip()) if v is not None else None for v in values]
        except ValueError:
            continue
        return converted
    return [v.strip() if v is not None else None for v in values]


def _to_bool(s: str) -> bool:
    low = s.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    raise ValueError(s)


def _to_int(s: str) -> int:
    if "_" in s:  # int() would accept Python's "1_000" literal syntax
        raise ValueError(s)
    return int(s)


def _to_float(s: str) -> float:
    if "_" in s or s.lower().lstrip("+-") in {"inf", "infinity", "nan"}:
        raise ValueError(s)
    return float(s)


def _to_date(s: str) -> date:
    if len(s) != 10:
        raise ValueError(s)
    return date.fromisoformat(s)


def _to_datetime(s: str) -> datetime:
    if len(s) < 16 or s[10] not in "T ":
        raise ValueError(s)
    return datetime.fromisoformat(s)


def _format(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)
