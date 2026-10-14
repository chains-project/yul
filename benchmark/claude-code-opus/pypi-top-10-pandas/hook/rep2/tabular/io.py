"""Reading and writing CSV files, with per-column type inference."""

from __future__ import annotations

import csv
import os
from collections.abc import Collection, Sequence
from typing import Any

from tabular.table import Table

DEFAULT_MISSING = frozenset({"", "na", "n/a", "nan", "null", "none", "-"})
_TRUE = frozenset({"true", "yes", "y"})
_FALSE = frozenset({"false", "no", "n"})


def load_csv(
    path: str | os.PathLike[str],
    *,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    infer_types: bool = True,
    missing_values: Collection[str] = DEFAULT_MISSING,
) -> Table:
    """Load a CSV file with a header row into a :class:`Table`.

    The delimiter is sniffed from the file when not given. Cells matching
    ``missing_values`` (case-insensitive, ignoring surrounding whitespace)
    become ``None``. With ``infer_types``, each column is converted to the
    narrowest type that fits all of its values: bool, int, float, else str.
    Short rows are padded with ``None``; extra cells raise ``ValueError``.
    """
    with open(path, newline="", encoding=encoding) as f:
        sample = f.read(64 * 1024)
        f.seek(0)
        if delimiter is None:
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ","
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader, None)
        if header is None:
            return Table({})
        header = _dedupe_header(header)
        raw: list[list[str | None]] = [[] for _ in header]
        for line_no, record in enumerate(reader, start=2):
            if not record:
                continue
            if len(record) > len(header):
                raise ValueError(
                    f"{path}: line {line_no} has {len(record)} fields, header has {len(header)}"
                )
            record = record + [None] * (len(header) - len(record))
            for column, cell in zip(raw, record):
                column.append(cell)

    missing = {token.lower() for token in missing_values}
    columns: dict[str, list[Any]] = {}
    for name, cells in zip(header, raw):
        values = [None if c is None or c.strip().lower() in missing else c for c in cells]
        columns[name] = infer_column(values) if infer_types else values
    return Table(columns)


def save_csv(table: Table, path: str | os.PathLike[str], *, delimiter: str = ",", encoding: str = "utf-8") -> None:
    """Write a table to CSV. ``None`` is written as an empty cell."""
    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(table.columns)
        for row in table.rows():
            writer.writerow("" if value is None else value for value in row.values())


def infer_column(values: Sequence[str | None]) -> list[Any]:
    """Convert string cells to the narrowest type shared by every non-missing value."""
    present = [value.strip() for value in values if value is not None]
    if not present:
        return list(values)
    for parse in (_parse_bool, _parse_int, _parse_float):
        try:
            parsed = [parse(value) for value in present]
        except ValueError:
            continue
        it = iter(parsed)
        return [None if value is None else next(it) for value in values]
    return list(values)


def _parse_bool(text: str) -> bool:
    lowered = text.lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ValueError(text)


def _parse_int(text: str) -> int:
    _reject_leading_zero(text)
    return int(text.replace(",", "") if _is_grouped(text) else text)


def _parse_float(text: str) -> float:
    _reject_leading_zero(text)
    value = float(text.replace(",", "") if _is_grouped(text) else text)
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError(text)
    return value


def _reject_leading_zero(text: str) -> None:
    """Leading zeros (ZIP codes, IDs like ``007``) signal an identifier, not a number."""
    whole = text.lstrip("+-").split(".", 1)[0]
    if len(whole) > 1 and whole.startswith("0"):
        raise ValueError(text)


def _is_grouped(text: str) -> bool:
    """True for thousands-grouped numbers like ``1,234,567.8``."""
    whole = text.lstrip("+-").split(".", 1)[0]
    groups = whole.split(",")
    return (
        len(groups) > 1
        and 1 <= len(groups[0]) <= 3
        and all(len(g) == 3 and g.isdigit() for g in groups[1:])
        and groups[0].isdigit()
    )


def _dedupe_header(header: list[str]) -> list[str]:
    """Strip names, name blank columns, and suffix duplicates (``a``, ``a_2``)."""
    seen: dict[str, int] = {}
    result = []
    for index, name in enumerate(header):
        name = name.strip() or f"column_{index + 1}"
        base = name
        while name in seen:
            seen[base] += 1
            name = f"{base}_{seen[base]}"
        seen.setdefault(name, 1)
        result.append(name)
    return result
