"""Reading and writing CSV files, with automatic type inference."""

from __future__ import annotations

import csv
import io
import os
import re
from datetime import date, datetime
from typing import Any, Iterable, Sequence

from .table import Table

DEFAULT_NA_VALUES = frozenset({"", "na", "n/a", "nan", "null", "none", "-", "?"})
_TRUE = {"true", "yes", "y", "t"}
_FALSE = {"false", "no", "n", "f"}
_DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y")
_DATETIME_FORMATS = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")


# Commas are accepted only as well-formed thousands separators ("1,234,567"), so
# a European decimal such as "1,5" stays a string instead of becoming 15.
_THOUSANDS = re.compile(r"[+-]?\d{1,3}(,\d{3})+(\.\d*)?")


def _strip_thousands(s: str) -> str:
    s = s.strip()
    return s.replace(",", "") if _THOUSANDS.fullmatch(s) else s


def _parse_int(s: str) -> int:
    s = _strip_thousands(s)
    if not s.lstrip("+-").isdigit():
        raise ValueError(s)
    return int(s)


def _parse_float(s: str) -> float:
    return float(_strip_thousands(s))


def _parse_bool(s: str) -> bool:
    low = s.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    raise ValueError(s)


def _parse_with_formats(s: str, formats: Sequence[str], as_date: bool) -> Any:
    for fmt in formats:
        try:
            parsed = datetime.strptime(s, fmt)
            return parsed.date() if as_date else parsed
        except ValueError:
            continue
    raise ValueError(s)


def _parse_date(s: str) -> date:
    return _parse_with_formats(s, _DATE_FORMATS, as_date=True)


def _parse_datetime(s: str) -> datetime:
    return _parse_with_formats(s, _DATETIME_FORMATS, as_date=False)


# Order matters: the first parser that accepts every non-missing value wins.
_PARSERS = (
    ("int", _parse_int),
    ("float", _parse_float),
    ("bool", _parse_bool),
    ("date", _parse_date),
    ("datetime", _parse_datetime),
)


def infer_column(values: Sequence[str | None]) -> tuple[str, list[Any]]:
    """Return ``(type_name, converted_values)`` for a column of raw strings."""
    present = [v for v in values if v is not None]
    if not present:
        return "str", list(values)
    for name, parser in _PARSERS:
        try:
            converted = [None if v is None else parser(v) for v in values]
        except (ValueError, OverflowError):
            continue
        return name, converted
    return "str", list(values)


def _build_table(
    rows: Iterable[list[str]],
    header: bool,
    na_values: Iterable[str] | None,
    infer_types: bool,
    skip_blank_lines: bool,
) -> Table:
    na = {v.strip().lower() for v in (DEFAULT_NA_VALUES if na_values is None else na_values)}
    rows = [r for r in rows if not (skip_blank_lines and all(not c.strip() for c in r))]
    if not rows:
        return Table({})

    if header:
        names, body = rows[0], rows[1:]
    else:
        width = max(len(r) for r in rows)
        names, body = [f"column_{i}" for i in range(width)], rows

    names = _dedupe_names([n.strip() or f"column_{i}" for i, n in enumerate(names)])
    width = len(names)
    columns: dict[str, list[Any]] = {n: [] for n in names}
    for lineno, row in enumerate(body, start=2 if header else 1):
        if len(row) > width:
            raise ValueError(f"row {lineno} has {len(row)} fields, expected {width}")
        row = row + [""] * (width - len(row))  # pad ragged short rows
        for name, cell in zip(names, row):
            columns[name].append(None if cell.strip().lower() in na else cell)

    if infer_types:
        columns = {n: infer_column(v)[1] for n, v in columns.items()}
    return Table(columns)


def _dedupe_names(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for n in names:
        if n in seen:
            seen[n] += 1
            n = f"{n}_{seen[n]}"
        seen.setdefault(n, 0)
        out.append(n)
    return out


def read_csv_text(
    text: str,
    delimiter: str | None = None,
    header: bool = True,
    na_values: Iterable[str] | None = None,
    infer_types: bool = True,
    skip_blank_lines: bool = True,
) -> Table:
    """Parse CSV content from a string. See :func:`load_csv` for parameters."""
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    return _build_table(reader, header, na_values, infer_types, skip_blank_lines)


def load_csv(
    path: str | os.PathLike,
    delimiter: str | None = None,
    header: bool = True,
    encoding: str = "utf-8-sig",
    na_values: Iterable[str] | None = None,
    infer_types: bool = True,
    skip_blank_lines: bool = True,
) -> Table:
    """Load a CSV file into a :class:`Table`.

    Args:
        path: File to read.
        delimiter: Field separator; sniffed from the content when ``None``.
        header: Whether the first row contains column names.
        encoding: File encoding. The default strips a UTF-8 BOM if present.
        na_values: Strings (case-insensitive) treated as missing. Defaults to
            ``DEFAULT_NA_VALUES``; pass an empty list to disable.
        infer_types: Convert columns to int/float/bool/date/datetime when every
            non-missing value parses as that type.
        skip_blank_lines: Ignore rows where every field is empty.
    """
    with open(path, newline="", encoding=encoding) as f:
        text = f.read()
    return read_csv_text(text, delimiter, header, na_values, infer_types, skip_blank_lines)


def write_csv(table: Table, path: str | os.PathLike, delimiter: str = ",", encoding: str = "utf-8") -> None:
    """Write a Table to CSV. Missing values are written as empty fields."""
    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(table.columns)
        for row in table.rows():
            writer.writerow(["" if v is None else _format(v) for v in row.values()])


def _format(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)
