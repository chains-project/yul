"""CSV loading helpers for :mod:`datalab`."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, TextIO, Union

from .table import Table

__all__ = ["load_csv", "load_rows", "make_unique_headers"]

PathLike = Union[str, "os.PathLike[str]"]


def make_unique_headers(headers: Sequence[str]) -> List[str]:
    """Return *headers* with duplicates and blanks made unique.

    Blank names become ``column_1``, ``column_2`` ... and repeated names are
    suffixed with ``_2``, ``_3`` ... so the result is always safe to use with
    :class:`~datalab.table.Table`.
    """
    seen: dict[str, int] = {}
    result: List[str] = []
    for position, header in enumerate(headers, start=1):
        name = str(header).replace("\ufeff", "").strip() if header is not None else ""
        if not name:
            name = f"column_{position}"
        if name in seen:
            seen[name] += 1
            candidate = f"{name}_{seen[name]}"
            while candidate in seen:
                seen[name] += 1
                candidate = f"{name}_{seen[name]}"
            name = candidate
        seen[name] = 1
        result.append(name)
    return result


def _open_csv(source: Union[PathLike, TextIO], encoding: str):
    if hasattr(source, "read"):
        return source, False
    path = Path(source)
    handle = open(path, "r", encoding=encoding, newline="")
    return handle, True


def _is_blank(row: Sequence[Any]) -> bool:
    return all(cell is None or str(cell).strip() == "" for cell in row)


def load_rows(
    rows: Iterable[Sequence[Any]],
    *,
    has_header: bool = True,
    skip_blank_lines: bool = True,
    make_unique: bool = True,
    headers: Optional[Sequence[str]] = None,
) -> Table:
    """Build a :class:`Table` from an iterable of row sequences."""
    buffered = list(rows)
    if skip_blank_lines:
        buffered = [row for row in buffered if not _is_blank(row)]

    if has_header:
        if not buffered:
            raise ValueError("cannot load a table from empty data")
        raw_headers = list(headers) if headers is not None else list(buffered[0])
        data_rows = buffered[1:]
    else:
        raw_headers = list(headers) if headers is not None else []
        data_rows = buffered

    if not raw_headers:
        width = max((len(row) for row in data_rows), default=0)
        raw_headers = [f"column_{i}" for i in range(1, width + 1)]

    final_headers = make_unique_headers(raw_headers) if make_unique else list(raw_headers)
    return Table(final_headers, data_rows)


def load_csv(
    source: Union[PathLike, TextIO],
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    has_header: bool = True,
    skip_blank_lines: bool = True,
    make_unique: bool = True,
    quotechar: str = '"',
) -> Table:
    """Load a CSV file (or file object) into a :class:`Table`.

    Parameters
    ----------
    source:
        A filesystem path or an open text file object.
    delimiter:
        Field delimiter, ``","`` by default.
    encoding:
        Text encoding used when *source* is a path.  ``utf-8-sig`` silently
        strips a leading byte-order mark.
    has_header:
        When ``True`` the first record provides the column names.  Otherwise
        names are auto-generated as ``column_1``, ``column_2`` ...
    skip_blank_lines:
        Drop records where every field is empty.
    make_unique:
        Rename blank/duplicate headers so the resulting table is valid.
    quotechar:
        Quote character understood by :mod:`csv`.
    """
    handle, should_close = _open_csv(source, encoding)
    try:
        reader = csv.reader(handle, delimiter=delimiter, quotechar=quotechar)
        return load_rows(
            reader,
            has_header=has_header,
            skip_blank_lines=skip_blank_lines,
            make_unique=make_unique,
        )
    finally:
        if should_close:
            handle.close()
