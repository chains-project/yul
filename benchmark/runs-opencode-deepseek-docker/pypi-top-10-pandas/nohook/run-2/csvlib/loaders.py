"""Loading CSV data into :class:`~csvlib.table.Table` objects."""

from __future__ import annotations

import csv
import io
import os
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, Optional

from ._utils import uniquify
from .table import Table

#: Tokens that are treated as missing values by default.
DEFAULT_MISSING = ("", "na", "n/a", "null", "none", "nan", "nil", "missing", "-", "--")

_DELIMITER_CANDIDATES = (",", ";", "\t", "|")


@contextmanager
def _read_text(source: Any, encoding: Optional[str]) -> Iterator[str]:
    """Yield the text content of a path, file object, or bytes."""
    if isinstance(source, bytes):
        yield source.decode(encoding or "utf-8-sig")
    elif hasattr(source, "read"):
        data = source.read()
        if isinstance(data, bytes):
            data = data.decode(encoding or "utf-8-sig")
        yield data
    elif isinstance(source, (str, os.PathLike)):
        with open(os.fspath(source), "r", encoding=encoding or "utf-8-sig", newline="") as fh:
            yield fh.read()
    else:
        raise TypeError(
            f"source must be a path, file object or bytes, not {type(source).__name__}"
        )


def _guess_delimiter(text: str) -> str:
    sample = text[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(_DELIMITER_CANDIDATES)).delimiter
    except csv.Error:
        counts = {d: sample.count(d) for d in _DELIMITER_CANDIDATES}
        best = max(counts, key=counts.get)
        return best if counts[best] else ","


def _missing_set(missing: Optional[Iterable[str]]) -> frozenset[str]:
    if missing is None:
        return frozenset()
    return frozenset(m.lower() for m in missing)


def _clean_value(value: Any, missing: frozenset[str]) -> Any:
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in missing:
            return None
    return value


def _header_names(header: list[str], strip: bool) -> list[str]:
    names = []
    for index, name in enumerate(header):
        name = name.strip() if strip else name
        names.append(name if name else f"column_{index + 1}")
    return uniquify(names)


def parse_csv(
    text: str,
    *,
    delimiter: Optional[str] = None,
    has_header: bool = True,
    missing: Optional[Iterable[str]] = DEFAULT_MISSING,
    sniff: bool = True,
    strip_headers: bool = True,
) -> Table:
    """Parse CSV *text* into a :class:`Table`.

    If *delimiter* is ``None`` and *sniff* is true the delimiter is detected
    automatically.  Values equal to any token in *missing* (case-insensitive)
    become ``None``.
    """
    if not text.strip():
        return Table([])

    delimiter = delimiter or (_guess_delimiter(text) if sniff else ",")
    raw_rows = [row for row in csv.reader(io.StringIO(text), delimiter=delimiter)]
    if not raw_rows:
        return Table([])

    if has_header:
        columns = _header_names(raw_rows[0], strip_headers)
        data = raw_rows[1:]
    else:
        width = max(len(row) for row in raw_rows)
        columns = [f"column_{i + 1}" for i in range(width)]
        data = raw_rows

    missing_set = _missing_set(missing)
    rows: list[list[Any]] = []
    width = len(columns)
    for raw in data:
        if len(raw) < width:
            raw = raw + [None] * (width - len(raw))
        elif len(raw) > width:
            raw = raw[:width]
        rows.append([_clean_value(value, missing_set) for value in raw])
    return Table(columns, rows)


def load_csv(
    source: Any,
    *,
    delimiter: Optional[str] = None,
    encoding: Optional[str] = None,
    has_header: bool = True,
    missing: Optional[Iterable[str]] = DEFAULT_MISSING,
    sniff: bool = True,
    strip_headers: bool = True,
) -> Table:
    """Load a CSV file from *source* into a :class:`Table`.

    *source* may be a filesystem path (``str``/``os.PathLike``), an open text
    or binary file object, or raw ``bytes``.  ``utf-8-sig`` is used by default
    so byte-order marks are handled transparently.
    """
    with _read_text(source, encoding) as text:
        return parse_csv(
            text,
            delimiter=delimiter,
            has_header=has_header,
            missing=missing,
            sniff=sniff,
            strip_headers=strip_headers,
        )


def load_csvs(
    sources: Iterable[Any],
    *,
    source_column: Optional[str] = None,
    **kwargs: Any,
) -> Table:
    """Load and concatenate multiple CSV sources.

    Columns are unioned in order of first appearance; absent values become
    ``None``.  When *source_column* is given, a column with that name is added
    holding each row's source label.
    """
    tables = []
    labels = []
    for source in sources:
        labels.append(_source_label(source))
        tables.append(load_csv(source, **kwargs))
    if not tables:
        return Table([])

    columns: list[str] = []
    for table in tables:
        for column in table.columns:
            if column not in columns:
                columns.append(column)

    rows: list[list[Any]] = []
    for table, label in zip(tables, labels):
        for row in table:
            values = [row.get(column) for column in columns]
            if source_column is not None:
                values.append(label)
            rows.append(values)

    if source_column is not None:
        columns.append(source_column)
    return Table(columns, rows)


def _source_label(source: Any) -> Any:
    if isinstance(source, (str, os.PathLike)):
        return os.fspath(source)
    return getattr(source, "name", None)
