"""Reading and writing CSV files."""

from __future__ import annotations

import csv
import io
import os
import re
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, List, Optional, Sequence, TextIO, Union

from .table import Table

DEFAULT_MISSING = ("", "na", "n/a", "nan", "null", "none")

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")

PathLike = Union[str, "os.PathLike[str]"]


def infer_value(
    value: Any,
    missing: Iterable[str] = DEFAULT_MISSING,
) -> Any:
    """Infer a Python type for a raw string value.

    Empty/missing tokens become ``None``. Integer and float literals are
    converted to ``int``/``float``, ``true``/``false`` to ``bool`` and
    everything else is left as a string. Strings with leading zeros (for
    example ``"007"``) are preserved as strings to avoid losing information.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return value

    token = value.strip()
    lowered = token.lower()
    if lowered in {item.lower() for item in missing}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_RE.match(token):
        digits = token.lstrip("+-")
        if len(digits) > 1 and digits.startswith("0"):
            return token
        return int(token)
    if _FLOAT_RE.match(token):
        return float(token)
    return value


def coerce_value(value: Any, target: str) -> Any:
    """Coerce ``value`` to the type named by ``target``.

    Supported targets: ``"str"``, ``"int"``, ``"float"``, ``"bool"`` and
    ``"auto"`` (infer). ``None`` is preserved for all targets. Values that
    cannot be converted raise :class:`ValueError`.
    """
    if value is None:
        return None

    target = target.lower()
    if target == "auto":
        return infer_value(value)
    if target == "str":
        return value if isinstance(value, str) else str(value)
    if target == "int":
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, str):
            value = value.strip()
            if validate_missing(value):
                return None
        return int(float(value)) if isinstance(value, str) and "." in value else int(value)
    if target == "float":
        if isinstance(value, str):
            value = value.strip()
            if validate_missing(value):
                return None
        return float(value)
    if target == "bool":
        if isinstance(value, bool):
            return value
        token = str(value).strip().lower()
        if token in ("true", "1", "yes", "y"):
            return True
        if token in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"cannot convert {value!r} to bool")
    raise ValueError(f"unknown type target: {target!r}")


def validate_missing(token: str) -> bool:
    return token.strip().lower() in DEFAULT_MISSING


@contextmanager
def _open_source(source: Union[PathLike, TextIO], encoding: str) -> Iterator[TextIO]:
    if hasattr(source, "read"):
        yield source  # type: ignore[misc]
        return
    with open(source, "r", encoding=encoding, newline="") as handle:
        yield handle


def _unique_columns(names: Sequence[str]) -> List[str]:
    result: List[str] = []
    seen = {}
    for name in names:
        if name not in seen:
            seen[name] = 0
            result.append(name)
            continue
        seen[name] += 1
        candidate = f"{name}_{seen[name]}"
        while candidate in seen:
            seen[name] += 1
            candidate = f"{name}_{seen[name]}"
        seen[candidate] = 0
        result.append(candidate)
    return result


def read_csv(
    source: Union[PathLike, TextIO],
    delimiter: str = ",",
    encoding: str = "utf-8",
    header: bool = True,
    infer_types: bool = True,
    skip_blank_lines: bool = True,
    missing_values: Optional[Iterable[str]] = None,
) -> Table:
    """Load a CSV file into a :class:`~tabular.table.Table`.

    Parameters
    ----------
    source:
        A filesystem path or an already-open text file object.
    delimiter:
        Field delimiter.
    header:
        When true the first non-blank row provides column names, otherwise
        columns are named ``col_1`` ... ``col_n``.
    infer_types:
        When true, numeric/boolean/missing values are inferred, otherwise all
        values remain strings.
    skip_blank_lines:
        Ignore rows whose cells are all empty.
    missing_values:
        Extra tokens (in addition to the defaults) treated as missing.
    """
    missing = set(DEFAULT_MISSING)
    if missing_values:
        missing.update(token.strip().lower() for token in missing_values)

    with _open_source(source, encoding) as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        rows = []
        for raw in reader:
            if skip_blank_lines and all(cell.strip() == "" for cell in raw):
                continue
            rows.append(raw)

    if not rows:
        return Table([], {})

    width = max(len(row) for row in rows)
    if header:
        header_row = rows[0]
        header_row = header_row + [""] * (width - len(header_row))
        columns = _unique_columns(
            [name.strip() if name.strip() else f"col_{i + 1}" for i, name in enumerate(header_row)]
        )
        body = rows[1:]
    else:
        columns = [f"col_{i + 1}" for i in range(width)]
        body = rows

    data: dict = {name: [] for name in columns}
    for row in body:
        padded = row + [""] * (width - len(row))
        for name, cell in zip(columns, padded):
            if infer_types:
                value = infer_value(cell, missing)
            else:
                stripped = cell.strip()
                value = None if stripped.lower() in missing else cell
            data[name].append(value)

    return Table(columns, data)


def read_csv_string(
    text: str,
    **kwargs: Any,
) -> Table:
    """Convenience wrapper around :func:`read_csv` for CSV content in a string."""
    kwargs.pop("encoding", None)
    return read_csv(io.StringIO(text), **kwargs)


def write_csv(
    table: Table,
    destination: Union[PathLike, TextIO],
    delimiter: str = ",",
    encoding: str = "utf-8",
    include_header: bool = True,
) -> None:
    """Write ``table`` to a CSV file.

    ``destination`` may be a filesystem path or a writable text file object.
    ``None`` values are written as empty fields.
    """
    close = False
    if hasattr(destination, "write"):
        handle = destination  # type: ignore[assignment]
    else:
        handle = open(destination, "w", encoding=encoding, newline="")
        close = True

    try:
        writer = csv.writer(handle, delimiter=delimiter)
        if include_header:
            writer.writerow(table.columns)
        for row in table.rows():
            writer.writerow(["" if value is None else value for value in row])
    finally:
        if close:
            handle.close()
