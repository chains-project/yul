"""Load delimited text (CSV) into a :class:`~tabular.table.Table`."""

from __future__ import annotations

import csv
import io
import os
from typing import Any, Iterable, Sequence

from .table import Table

_MISSING = {"", "na", "n/a", "nan", "null", "none", "-"}


def _open_stream(source: Any, encoding: str):
    """Return a text stream for a path or file-like object."""
    if isinstance(source, (str, os.PathLike)):
        return open(source, "r", encoding=encoding, newline="")
    if isinstance(source, io.TextIOBase):
        return source
    if isinstance(source, io.IOBase) or hasattr(source, "read"):
        return io.TextIOWrapper(source, encoding=encoding, newline="")
    raise TypeError(f"unsupported source type: {type(source)!r}")


def infer_type(value: str) -> Any:
    """Best-effort scalar conversion for a raw CSV field.

    Empty/known-null strings become ``None``. Values that look like integers
    (including negatives) become ``int``; decimals/scientific notation become
    ``float``; everything else stays ``str``. Leading-zero codes such as zip
    codes are preserved as strings.
    """
    text = value.strip()
    if text.lower() in _MISSING:
        return None
    try:
        if text.lstrip("+-").isdigit():
            if len(text.lstrip("+-")) > 1 and text.lstrip("+-").startswith("0"):
                return text
            return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def _infer_column(values: list[str]) -> list[Any]:
    converted = [infer_type(v) for v in values]
    # Only keep numeric conversion if *all* non-missing cells converted.
    non_missing = [v for v in converted if v is not None]
    if non_missing and not all(
        isinstance(v, (int, float)) and not isinstance(v, bool)
        for v in non_missing
    ):
        return [None if v is None else str(v).strip() for v in values]
    return converted


def _normalize_headers(headers: Sequence[str]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for i, raw in enumerate(headers):
        name = raw.strip() or f"column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        result.append(name)
    return result


def load_csv(
    source: Any,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    has_header: bool = True,
    infer_types: bool = True,
    skip_blank_lines: bool = True,
) -> Table:
    """Load a CSV file (path or file-like) into a :class:`Table`.

    Args:
        source: Filesystem path or readable text/binary stream.
        delimiter: Field separator, e.g. ``\\t`` for TSV.
        encoding: Text encoding used when ``source`` is a path/binary stream.
        has_header: Treat the first row as column names. When ``False``,
            columns are named ``column_1``..``column_n``.
        infer_types: Convert numeric/null-looking fields to ``int``/``float``
            /``None``. When ``False`` every cell stays a ``str``.
        skip_blank_lines: Ignore fully empty lines.
    """
    stream = _open_stream(source, encoding)
    close = stream is not source and not isinstance(source, io.TextIOBase)
    try:
        reader = csv.reader(stream, delimiter=delimiter)
        records = [row for row in reader if row or not skip_blank_lines]
    finally:
        if close:
            stream.close()

    if not records:
        return Table([])

    if has_header:
        columns = _normalize_headers(records[0])
        data = records[1:]
    else:
        width = max(len(r) for r in records)
        columns = [f"column_{i + 1}" for i in range(width)]
        data = records

    width = len(columns)
    padded: list[list[str]] = []
    for row in data:
        if len(row) < width:
            row = row + [""] * (width - len(row))
        elif len(row) > width:
            row = row[:width]
        padded.append([cell.strip() for cell in row])

    if infer_types:
        matrix = [
            _infer_column([row[i] for row in padded]) for i in range(width)
        ]
        rows = [[matrix[i][r] for i in range(width)] for r in range(len(padded))]
    else:
        rows = padded

    return Table(columns, rows)


def load_rows(
    records: Iterable[dict[str, Any]], columns: Sequence[str] | None = None
) -> Table:
    """Build a :class:`Table` from an iterable of mappings (e.g. sqlite rows)."""
    records = list(records)
    if columns is None:
        columns = list(records[0].keys()) if records else []
    rows = [[record.get(name) for name in columns] for record in records]
    return Table(columns, rows)
