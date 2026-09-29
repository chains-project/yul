"""Reading and writing CSV files."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from os import PathLike
from typing import IO, Any

from .table import Table

Source = str | bytes | PathLike[str] | IO[str]


def _sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def _read_rows(
    handle: IO[str],
    *,
    delimiter: str | None,
    quotechar: str,
    has_header: bool,
) -> Table:
    if delimiter is None:
        sample = handle.read(4096)
        handle.seek(0)
        delimiter = _sniff_delimiter(sample)

    reader = csv.reader(handle, delimiter=delimiter, quotechar=quotechar)
    records = [row for row in reader if row]

    if not records:
        return Table([] if has_header else [], [])

    if has_header:
        headers = [value.strip() for value in records[0]]
        body = records[1:]
    else:
        width = max(len(row) for row in records)
        headers = [f"column_{i + 1}" for i in range(width)]
        body = records

    return Table(headers, body)


def load_csv(
    source: Source,
    *,
    delimiter: str | None = ",",
    quotechar: str = '"',
    encoding: str = "utf-8",
    has_header: bool = True,
) -> Table:
    """Load a CSV file into a :class:`~tabular.table.Table`.

    ``source`` may be a filesystem path or an already-open text stream. Pass
    ``delimiter=None`` to sniff the delimiter automatically. Missing values are
    left as empty strings; use :func:`tabular.cleaning.replace_missing` to turn
    them into ``None``.
    """
    if hasattr(source, "read"):
        return _read_rows(
            source, delimiter=delimiter, quotechar=quotechar, has_header=has_header
        )

    if isinstance(source, (str, bytes, PathLike)):
        with open(source, "r", newline="", encoding=encoding) as handle:
            return _read_rows(
                handle,
                delimiter=delimiter,
                quotechar=quotechar,
                has_header=has_header,
            )

    raise TypeError(f"unsupported CSV source: {type(source).__name__}")


def load_csvs(
    sources: Iterable[Source],
    *,
    delimiter: str | None = ",",
    quotechar: str = '"',
    encoding: str = "utf-8",
    has_header: bool = True,
) -> Table:
    """Load and vertically stack several CSV sources with identical headers."""
    tables = [
        load_csv(
            source,
            delimiter=delimiter,
            quotechar=quotechar,
            encoding=encoding,
            has_header=has_header,
        )
        for source in sources
    ]
    if not tables:
        return Table([], [])

    headers = tables[0].headers
    rows: list[list[Any]] = []
    for table in tables:
        if table.headers != headers:
            raise ValueError("all CSV sources must share the same headers")
        rows.extend(table.rows)
    return Table(headers, rows)


def write_csv(
    table: Table,
    destination: str | bytes | PathLike[str] | IO[str] | None = None,
    *,
    delimiter: str = ",",
    quotechar: str = '"',
    encoding: str = "utf-8",
) -> str | None:
    """Write ``table`` as CSV.

    When ``destination`` is ``None`` the CSV text is returned as a string;
    otherwise it is written to the given path or stream and ``None`` is
    returned.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, quotechar=quotechar)
    writer.writerow(table.headers)
    writer.writerows(table.rows)
    text = buffer.getvalue()

    if destination is None:
        return text

    if hasattr(destination, "write"):
        destination.write(text)
        return None

    with open(destination, "w", newline="", encoding=encoding) as handle:
        handle.write(text)
    return None
