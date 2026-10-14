"""Loading tabular data from CSV files."""

from __future__ import annotations

import csv
import io
import os
from typing import Any, Iterable

from .table import Table

DEFAULT_NA_VALUES = frozenset({"", "na", "n/a", "nan", "null", "none", "-", "?"})
_TRUE = {"true", "yes", "y", "t"}
_FALSE = {"false", "no", "n", "f"}


def _is_na(value: str, na_values: frozenset[str]) -> bool:
    return value.strip().lower() in na_values


def _parse_int(s: str) -> int:
    # Python's int()/float() accept "1_000"; CSV data shouldn't.
    if "_" in s:
        raise ValueError(s)
    return int(s)


def _parse_float(s: str) -> float:
    if "_" in s:
        raise ValueError(s)
    return float(s)


def _parse_bool(s: str) -> bool:
    v = s.strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(s)


_PARSERS = {"int": _parse_int, "float": _parse_float, "bool": _parse_bool, "str": lambda s: s}


def infer_type(values: Iterable[str]) -> str:
    """Return the narrowest of 'int', 'float', 'bool', 'str' that fits all values.

    ``values`` should already exclude missing entries. An empty column is 'str'.
    """
    values = list(values)
    if not values:
        return "str"
    for name in ("int", "float", "bool"):
        parser = _PARSERS[name]
        try:
            for v in values:
                parser(v)
        except ValueError:
            continue
        return name
    return "str"


def parse_value(value: str, type_name: str) -> Any:
    return _PARSERS[type_name](value)


def _read_rows(text: str, delimiter: str | None) -> list[list[str]]:
    if delimiter is None:
        sample = text[:64 * 1024]
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    return list(csv.reader(io.StringIO(text), delimiter=delimiter))


def read_csv(
    source: str | os.PathLike[str] | io.TextIOBase,
    *,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    header: bool = True,
    na_values: Iterable[str] | None = None,
    infer_types: bool = True,
    dtypes: dict[str, str] | None = None,
) -> Table:
    """Load a CSV file into a :class:`Table`.

    Args:
        source: A file path or an open text file object.
        delimiter: Field separator; sniffed from the data when ``None``.
        encoding: File encoding (``utf-8-sig`` transparently strips a BOM).
        header: Whether the first row holds column names. If ``False``,
            columns are named ``column_1``, ``column_2``, ...
        na_values: Strings (case-insensitive) treated as missing and loaded
            as ``None``. Defaults to :data:`DEFAULT_NA_VALUES`.
        infer_types: Convert columns to int/float/bool where every non-missing
            value fits. When ``False`` all values stay strings.
        dtypes: Explicit per-column type ('int', 'float', 'bool', 'str'),
            overriding inference. Raises ``ValueError`` if a value won't parse.

    Short rows are padded with missing values; rows longer than the header
    raise ``ValueError``. Fully blank lines are skipped.
    """
    if hasattr(source, "read"):
        text = source.read()
    else:
        with open(source, encoding=encoding, newline="") as f:
            text = f.read()

    na = frozenset(v.strip().lower() for v in na_values) if na_values is not None else DEFAULT_NA_VALUES
    raw = [r for r in _read_rows(text, delimiter) if any(cell.strip() for cell in r)]
    if not raw:
        return Table([])

    if header:
        columns = [c.strip() for c in raw[0]]
        body = raw[1:]
    else:
        columns = [f"column_{i + 1}" for i in range(max(len(r) for r in raw))]
        body = raw
    columns = _dedupe_names(columns)

    width = len(columns)
    rows: list[list[str | None]] = []
    for lineno, r in enumerate(body, start=2 if header else 1):
        if len(r) > width:
            raise ValueError(f"row {lineno} has {len(r)} fields, expected at most {width}")
        r = r + [""] * (width - len(r))
        rows.append([None if _is_na(cell, na) else cell for cell in r])

    dtypes = dict(dtypes or {})
    unknown = set(dtypes) - set(columns)
    if unknown:
        raise KeyError(f"dtypes given for unknown columns: {sorted(unknown)}")
    for name, t in dtypes.items():
        if t not in _PARSERS:
            raise ValueError(f"unknown dtype {t!r} for column {name!r}")

    for i, col in enumerate(columns):
        values = [r[i] for r in rows if r[i] is not None]
        t = dtypes.get(col) or (infer_type(values) if infer_types else "str")
        if t == "str":
            continue
        for r in rows:
            if r[i] is not None:
                try:
                    r[i] = parse_value(r[i], t)
                except ValueError:
                    raise ValueError(f"column {col!r}: cannot parse {r[i]!r} as {t}") from None

    return Table(columns, rows)


def _dedupe_names(names: list[str]) -> list[str]:
    """Make column names unique and non-empty: ['a', 'a', ''] -> ['a', 'a_2', 'unnamed_3']."""
    seen: set[str] = set()
    out = []
    for i, name in enumerate(names):
        name = name or f"unnamed_{i + 1}"
        candidate, n = name, 2
        while candidate in seen:
            candidate = f"{name}_{n}"
            n += 1
        seen.add(candidate)
        out.append(candidate)
    return out


def write_csv(table: Table, path: str | os.PathLike[str], *, delimiter: str = ",", encoding: str = "utf-8") -> None:
    """Write a table to CSV; missing values are written as empty fields."""
    with open(path, "w", encoding=encoding, newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(table.columns)
        for row in table.rows:
            writer.writerow("" if v is None else v for v in row)
