"""Functions that turn CSV sources into :class:`~datalib.table.Table` objects."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any, Iterable

from .cleaning import NULL_TOKENS, coerce_types
from .exceptions import CSVParseError
from .table import Table


def _open_source(source, encoding: str):
    """Return ``(file_object, should_close)`` for a path or file-like source."""
    if hasattr(source, "read"):
        return source, False
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"no such file: {path}")
    return open(path, "r", encoding=encoding, newline=""), True


def _unique_names(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for raw in names:
        name = raw if raw != "" else "unnamed"
        if name in seen:
            seen[name] += 1
            candidate = f"{name}_{seen[name]}"
            while candidate in seen:
                seen[name] += 1
                candidate = f"{name}_{seen[name]}"
            name = candidate
        seen.setdefault(name, 1)
        result.append(name)
    return result


def _clean_cell(value: str, na_values: frozenset[str]) -> Any:
    stripped = value.strip()
    if stripped.lower() in na_values:
        return None
    return stripped


def load_csv(
    source,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    has_header: bool = True,
    strip: bool = True,
    infer_types: bool = False,
    na_values: Iterable[str] | None = None,
    skip_blank_lines: bool = True,
    strict: bool = False,
) -> Table:
    """Load a single CSV file (or file-like object) into a :class:`Table`.

    Parameters
    ----------
    source:
        A filesystem path or any object with a ``read`` method.
    delimiter:
        Field delimiter, e.g. ``","``, ``"\\t"`` or ``";"``.
    encoding:
        Text encoding; the default ``utf-8-sig`` also strips a BOM.
    has_header:
        When true the first record supplies the column names, otherwise names
        are generated as ``col_0``, ``col_1``, ...
    strip:
        Strip surrounding whitespace from every cell.
    infer_types:
        Infer and apply a type (``int``/``float``/``bool``/``date``) per column.
    na_values:
        Additional tokens to treat as missing, on top of the built-in set.
    skip_blank_lines:
        Ignore records where every field is empty.
    strict:
        Raise :class:`CSVParseError` on rows whose length differs from the
        header; otherwise short rows are padded and long rows truncated.
    """
    tokens = set(NULL_TOKENS)
    if na_values:
        tokens.update(t.lower() for t in na_values)
    na_set = frozenset(tokens)

    handle, should_close = _open_source(source, encoding)
    try:
        reader = csv.reader(handle, delimiter=delimiter)
        records = list(reader)
    except csv.Error as exc:  # pragma: no cover - defensive
        raise CSVParseError(str(exc)) from exc
    finally:
        if should_close:
            handle.close()

    if records and records[0]:
        records[0][0] = records[0][0].lstrip("\ufeff")

    if skip_blank_lines:
        records = [r for r in records if any(cell.strip() for cell in r)]
    if not records:
        if has_header:
            return Table([], [])
        return Table([], [])

    if has_header:
        header, data_records = records[0], records[1:]
        columns = _unique_names([h.strip() if strip else h for h in header])
    else:
        width = max(len(r) for r in records)
        columns = [f"col_{i}" for i in range(width)]
        data_records = records

    width = len(columns)
    rows = []
    for line_no, record in enumerate(data_records, start=2 if has_header else 1):
        if len(record) != width:
            if strict:
                raise CSVParseError(
                    f"row {line_no} has {len(record)} fields, expected {width}"
                )
            record = (record + [""] * width)[:width]
        rows.append([_clean_cell(cell, na_set) for cell in record])

    table = Table(columns, rows)

    if infer_types:
        table = coerce_types(table, infer=True)
    return table


def load_csvs(
    sources: Iterable,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    has_header: bool = True,
    **kwargs: Any,
) -> Table:
    """Load several CSVs and stack them into a single table.

    All input files must share the same header (order-insensitive); columns are
    unioned and missing values are filled with ``None``.
    """
    tables = [
        load_csv(
            source,
            delimiter=delimiter,
            encoding=encoding,
            has_header=has_header,
            **kwargs,
        )
        for source in sources
    ]
    if not tables:
        return Table([], [])

    columns: list[str] = []
    for table in tables:
        for name in table.columns:
            if name not in columns:
                columns.append(name)

    rows: list[dict[str, Any]] = []
    for table in tables:
        for row in table.rows:
            rows.append({name: row.get(name) for name in columns})
    return Table(columns, rows)


def load_csv_string(
    text: str,
    *,
    delimiter: str = ",",
    has_header: bool = True,
    **kwargs: Any,
) -> Table:
    """Parse CSV content already held in a string."""
    return load_csv(
        io.StringIO(text),
        delimiter=delimiter,
        has_header=has_header,
        **kwargs,
    )
