import csv
import io

from .table import Table

_TRUE_VALUES = {"true"}
_FALSE_VALUES = {"false"}


def load_csv(path, delimiter=",", encoding="utf-8", has_header=True, infer_types=True):
    with open(path, newline="", encoding=encoding) as handle:
        return _read(handle, delimiter, has_header, infer_types)


def load_csv_string(text, delimiter=",", has_header=True, infer_types=True):
    return _read(io.StringIO(text), delimiter, has_header, infer_types)


def coerce_value(value, infer_types=True):
    if value is None:
        return None
    text = value.strip() if isinstance(value, str) else value
    if text == "":
        return None
    if not infer_types or not isinstance(text, str):
        return text
    lowered = text.lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def _read(handle, delimiter, has_header, infer_types):
    reader = csv.reader(handle, delimiter=delimiter)
    try:
        first = next(reader)
    except StopIteration:
        return Table([], [])

    if has_header:
        columns = _unique_columns(first)
        data = list(reader)
    else:
        columns = _unique_columns([f"col{i + 1}" for i in range(len(first))])
        data = [first] + list(reader)

    rows = []
    for raw in data:
        row = {}
        for index, name in enumerate(columns):
            value = raw[index] if index < len(raw) else None
            row[name] = coerce_value(value, infer_types)
        rows.append(row)
    return Table(columns, rows)


def _unique_columns(names):
    seen = {}
    result = []
    for index, name in enumerate(names):
        name = name.strip() if isinstance(name, str) else name
        if not name:
            name = f"col{index + 1}"
        count = seen.get(name, 0)
        seen[name] = count + 1
        result.append(name if count == 0 else f"{name}_{count}")
    return result
