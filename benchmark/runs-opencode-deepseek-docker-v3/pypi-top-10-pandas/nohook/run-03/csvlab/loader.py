"""CSV loading with missing-value handling and type inference."""

from __future__ import annotations

import csv as _csv
import io
import os
import re
from typing import Any, Iterable, Sequence

from .table import Table

DEFAULT_MISSING = ("", "na", "n/a", "null", "none", "nan", "nil", "-")

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?$")
_TRUE = {"true", "yes"}
_FALSE = {"false", "no"}


def _clean_cell(value: Any, missing: frozenset[str], strip: bool) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip() if strip else value
        if text.lower() in missing:
            return None
        return text
    return value


def _classify(values: Sequence[Any]) -> str:
    present = [v for v in values if v is not None]
    if not present:
        return "str"
    if all(isinstance(v, bool) for v in present):
        return "bool"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in present):
        return "int"
    if all(
        isinstance(v, (int, float)) and not isinstance(v, bool) for v in present
    ) and any(isinstance(v, float) for v in present):
        return "float"
    if all(isinstance(v, str) for v in present):
        texts = [v.strip() for v in present if v.strip()]
        if texts and all(t.lower() in _TRUE | _FALSE for t in texts):
            return "bool"
        if all(_INT_RE.match(t) for t in texts):
            return "int"
        if all(_FLOAT_RE.match(t) for t in texts):
            return "float"
    return "str"


def _convert(value: Any, kind: str) -> Any:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    text = value.strip()
    if kind == "int":
        return int(text)
    if kind == "float":
        return float(text)
    if kind == "bool":
        return text.lower() in _TRUE
    return text


def _infer_column(values: list[Any]) -> list[Any]:
    kind = _classify(values)
    if kind == "str":
        return values
    return [_convert(v, kind) for v in values]


def load_csv(
    source: str | os.PathLike[str] | io.IOBase,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
    has_header: bool = True,
    missing_values: Iterable[str] = DEFAULT_MISSING,
    infer_types: bool = True,
    strip: bool = True,
    skip_blank_lines: bool = True,
) -> Table:
    """Load a CSV file into a :class:`~csvlab.table.Table`.

    ``source`` may be a filesystem path or an open text file object. Values
    matching ``missing_values`` (case-insensitive, after stripping) become
    ``None``. When ``infer_types`` is true each column is converted to ``int``,
    ``float``, or ``bool`` when every non-missing value qualifies.
    """

    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise ValueError("delimiter must be a single character")

    missing = frozenset(m.lower() for m in missing_values)

    close = False
    if isinstance(source, (str, os.PathLike)):
        handle: io.IOBase = open(source, "r", encoding=encoding, newline="")
        close = True
    elif hasattr(source, "read"):
        handle = source
        if isinstance(handle, io.TextIOBase) and hasattr(handle, "seek"):
            handle.seek(0)
    else:
        raise TypeError("source must be a path or an open file object")

    try:
        reader = _csv.reader(handle, delimiter=delimiter)
        raw_rows = []
        for row in reader:
            if skip_blank_lines and (not row or all(cell == "" for cell in row)):
                continue
            raw_rows.append(row)
    finally:
        if close:
            handle.close()

    if not raw_rows:
        return Table([], [])

    if has_header:
        columns = [str(c).strip() for c in raw_rows[0]]
        data = raw_rows[1:]
    else:
        width = max(len(r) for r in raw_rows)
        columns = [f"column_{i + 1}" for i in range(width)]
        data = raw_rows

    width = len(columns)
    normalised: list[list[Any]] = []
    for row in data:
        values = list(row)
        if len(values) < width:
            values.extend([None] * (width - len(values)))
        elif len(values) > width:
            values = values[:width]
        normalised.append([_clean_cell(v, missing, strip) for v in values])

    if not infer_types:
        return Table(columns, normalised)

    if not normalised:
        return Table(columns, [])

    inferred_columns = [_infer_column(list(col)) for col in zip(*normalised)]
    rows = [list(row) for row in zip(*inferred_columns)]
    return Table(columns, rows)


def load_csvs(
    sources: Iterable[str | os.PathLike[str]],
    **kwargs: Any,
) -> Table:
    """Load several CSVs and concatenate them, requiring identical headers."""

    frames = [load_csv(source, **kwargs) for source in sources]
    if not frames:
        return Table([], [])
    columns = frames[0].columns
    for frame in frames[1:]:
        if frame.columns != columns:
            raise ValueError(
                f"column mismatch: {frame.columns!r} != {columns!r}"
            )
    rows: list[list[Any]] = []
    for frame in frames:
        rows.extend(frame.to_rows())
    return Table(columns, rows)
