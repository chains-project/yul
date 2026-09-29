"""Read CSV sources into :class:`~csvdata.table.Table` objects."""

from __future__ import annotations

import csv
import io
import os

from .errors import CsvLoadError
from .table import Table
from .values import MISSING_TOKENS


def _normalise_missing(value, missing):
    if value is None:
        return None
    text = value.strip() if isinstance(value, str) else value
    if isinstance(text, str) and text.lower() in missing:
        return None
    return value


def _dedupe_headers(headers):
    seen = {}
    result = []
    for name in headers:
        key = name
        count = seen.get(key, 0)
        seen[key] = count + 1
        result.append(name if count == 0 else f"{name}_{count}")
    return result


def _parse(handle, delimiter, has_header, missing, max_rows):
    reader = csv.reader(handle, delimiter=delimiter)
    try:
        iterator = iter(reader)
        if has_header:
            try:
                header = next(iterator)
            except StopIteration:
                return Table([], [], {})
            columns = _dedupe_headers([cell.strip() for cell in header])
        else:
            first = next(iterator)
            columns = [f"column_{i + 1}" for i in range(len(first))]
            reader = _prepend(reader, first)
            iterator = iter(reader)
        rows = []
        for position, raw in enumerate(iterator, start=1):
            values = [_normalise_missing(cell, missing) for cell in raw]
            if len(values) > len(columns):
                raise CsvLoadError(
                    f"row {position} has {len(values)} fields but the header "
                    f"defines {len(columns)}"
                )
            if len(values) < len(columns):
                values.extend([None] * (len(columns) - len(values)))
            rows.append(values)
            if max_rows is not None and len(rows) >= max_rows:
                break
    except csv.Error as exc:
        raise CsvLoadError(f"could not parse CSV data: {exc}") from exc
    return Table(columns, rows, {column: "str" for column in columns})


def _prepend(reader, first_row):
    yield first_row
    yield from reader


def _read_source(source):
    if hasattr(source, "read"):
        return source
    if isinstance(source, bytes):
        return io.StringIO(source.decode("utf-8-sig"))
    raise TypeError("source must be a path, bytes, or a readable file object")


def load_csv(
    source,
    delimiter=",",
    encoding="utf-8-sig",
    has_header=True,
    missing_values=MISSING_TOKENS,
    max_rows=None,
):
    """Load tabular data from *source*.

    *source* may be a filesystem path, a ``bytes`` object, or a readable
    file-like object opened in text mode. Missing tokens are converted to
    ``None``; type inference and coercion are left to
    :func:`csvdata.cleaning.coerce_types` (or the :func:`csvdata.clean`
    convenience pipeline).
    """
    missing = frozenset(token.lower() for token in missing_values)
    if isinstance(source, (str, os.PathLike)):
        try:
            with open(source, "r", newline="", encoding=encoding) as handle:
                return _parse(handle, delimiter, has_header, missing, max_rows)
        except OSError as exc:
            raise CsvLoadError(f"could not read {source!r}: {exc}") from exc
    handle = _read_source(source)
    return _parse(handle, delimiter, has_header, missing, max_rows)


def load_csvs(sources, **kwargs):
    """Load several sources, returning ``{name: Table}``."""
    return {os.fspath(source): load_csv(source, **kwargs) for source in sources}
