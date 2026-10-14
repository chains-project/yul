"""Reading CSV data into a :class:`Table`."""

from __future__ import annotations

import csv
import io
import os
from typing import Iterable

from .cleaning import convert_column, infer_type
from .table import Table

_SNIFF_BYTES = 64 * 1024


def load_csv(
    path: str | os.PathLike,
    *,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    infer_types: bool = True,
    missing: Iterable[str] | None = None,
) -> Table:
    """Load a CSV file into a :class:`Table`.

    ``delimiter`` is detected automatically when not given. With
    ``infer_types`` each column is converted to int, float, bool, date, or
    left as str; values in ``missing`` (default :data:`MISSING_TOKENS`)
    become ``None``.
    """
    with open(path, newline="", encoding=encoding) as f:
        return read_csv_text(
            f.read(), delimiter=delimiter, infer_types=infer_types, missing=missing
        )


def read_csv_text(
    text: str,
    *,
    delimiter: str | None = None,
    infer_types: bool = True,
    missing: Iterable[str] | None = None,
) -> Table:
    """Parse CSV content held in a string. See :func:`load_csv`."""
    if delimiter is None:
        delimiter = _sniff_delimiter(text)
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    rows = [r for r in rows if any(cell.strip() for cell in r)]
    if not rows:
        return Table({})

    header = _dedupe_header([h.strip() for h in rows[0]])
    width = len(header)
    columns: dict[str, list] = {name: [] for name in header}
    for line_no, row in enumerate(rows[1:], start=2):
        if len(row) > width:
            raise ValueError(
                f"row {line_no} has {len(row)} fields, header has {width}"
            )
        row = row + [""] * (width - len(row))
        for name, cell in zip(header, row):
            columns[name].append(cell)

    if infer_types:
        missing_set = None if missing is None else {m.lower() for m in missing}
        for name, values in columns.items():
            kind = infer_type(values, missing_set)
            columns[name] = convert_column(values, kind, missing_set)
    return Table(columns)


def _sniff_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:_SNIFF_BYTES], delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def _dedupe_header(header: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for i, name in enumerate(header):
        name = name or f"column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        result.append(name)
    return result
