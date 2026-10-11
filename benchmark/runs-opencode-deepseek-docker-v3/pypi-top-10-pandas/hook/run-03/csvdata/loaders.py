"""Load tabular data from CSV files into :class:`~csvdata.table.Table`."""

from __future__ import annotations

import csv
from typing import Iterable, TextIO

from .table import Table


def _dedupe_headers(headers: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: dict[str, int] = {}
    for index, header in enumerate(headers):
        name = header.strip()
        if not name:
            name = f"column_{index + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        result.append(name)
    return result


def read_csv(
    source: TextIO | Iterable[str],
    *,
    delimiter: str = ",",
    has_header: bool = True,
) -> Table:
    """Read CSV records from an open stream or any iterable of lines.

    Blank trailing lines are ignored. When *has_header* is false the columns
    are named ``column_1``...``column_N``.
    """
    reader = csv.reader(source, delimiter=delimiter)
    records = [row for row in reader if any(cell.strip() for cell in row)]
    if not records:
        return Table([], [])

    if has_header:
        columns = _dedupe_headers(records[0])
        body = records[1:]
    else:
        width = max(len(row) for row in records)
        columns = [f"column_{i + 1}" for i in range(width)]
        body = records

    rows = []
    for record in body:
        record = list(record) + [""] * (len(columns) - len(record))
        rows.append(dict(zip(columns, record[: len(columns)])))
    return Table(columns, rows)


def load_csv(
    path: str,
    *,
    delimiter: str = ",",
    has_header: bool = True,
    encoding: str = "utf-8",
) -> Table:
    """Load a CSV file from *path* into a :class:`Table`."""
    with open(path, "r", encoding=encoding, newline="") as handle:
        return read_csv(handle, delimiter=delimiter, has_header=has_header)
