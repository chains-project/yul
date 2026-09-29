"""CSV loading helpers for the tabular package."""

from __future__ import annotations

import csv
import io
import os
from typing import Any, Iterable

from .errors import CSVLoadError
from .table import DataTable


def load_csv(
    source: Any,
    delimiter: str = ",",
    encoding: str = "utf-8",
    has_header: bool = True,
    skip_blank_lines: bool = True,
) -> DataTable:
    """Load a CSV file into a :class:`~tabular.DataTable`.

    ``source`` may be a filesystem path or any open file-like object exposing
    ``read``. When ``has_header`` is false, columns are named ``column_1`` ...
    ``column_n``. Short rows are padded with missing values; rows with more
    fields than the header raise :class:`~tabular.CSVLoadError`.
    """
    try:
        if hasattr(source, "read"):
            return _parse(source, delimiter, has_header, skip_blank_lines)
        with open(os.fspath(source), "r", encoding=encoding, newline="") as handle:
            return _parse(handle, delimiter, has_header, skip_blank_lines)
    except CSVLoadError:
        raise
    except OSError as exc:
        raise CSVLoadError(f"could not read {source!r}: {exc}") from exc


def load_csv_string(
    text: str,
    delimiter: str = ",",
    has_header: bool = True,
    skip_blank_lines: bool = True,
) -> DataTable:
    """Load CSV content from a string into a :class:`~tabular.DataTable`."""
    return _parse(io.StringIO(text), delimiter, has_header, skip_blank_lines)


def _parse(
    handle: Iterable[str],
    delimiter: str,
    has_header: bool,
    skip_blank_lines: bool,
) -> DataTable:
    try:
        parsed = list(csv.reader(handle, delimiter=delimiter))
    except csv.Error as exc:
        raise CSVLoadError(f"invalid CSV: {exc}") from exc

    if skip_blank_lines:
        parsed = [row for row in parsed if any(cell.strip() for cell in row)]
    if not parsed:
        raise CSVLoadError("CSV source contains no data")

    if has_header:
        header = _sanitize_header(parsed[0])
        data = parsed[1:]
    else:
        header = _sanitize_header(["" for _ in parsed[0]])
        data = parsed

    width = len(header)
    rows = [_fit_row(row, width) for row in data]
    return DataTable(header, rows)


def _sanitize_header(raw: Iterable[str]) -> list:
    header = []
    used = set()
    for index, name in enumerate(raw, start=1):
        base = (name or "").strip() or f"column_{index}"
        candidate = base
        counter = 1
        while candidate in used:
            candidate = f"{base}_{counter}"
            counter += 1
        used.add(candidate)
        header.append(candidate)
    return header


def _fit_row(row: list, width: int) -> list:
    if len(row) == width:
        return row
    if len(row) < width:
        return row + [None] * (width - len(row))
    raise CSVLoadError(f"row has {len(row)} fields but header has {width}")
