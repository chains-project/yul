from .table import Table


def strip_whitespace(table):
    rows = [
        {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()}
        for row in table.rows
    ]
    return Table(table.columns, rows)


def drop_duplicates(table):
    seen = set()
    rows = []
    for row in table.rows:
        key = tuple(row[name] for name in table.columns)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return Table(table.columns, rows)


def fill_missing(table, value=None, columns=None):
    names = _resolve_columns(table, columns)
    rows = []
    for row in table.rows:
        updated = dict(row)
        for name in names:
            if updated.get(name) is None:
                updated[name] = value
        rows.append(updated)
    return Table(table.columns, rows)


def drop_missing(table, columns=None, how="any"):
    if how not in {"any", "all"}:
        raise ValueError("how must be 'any' or 'all'")
    names = _resolve_columns(table, columns)
    rows = []
    for row in table.rows:
        missing = [name for name in names if row.get(name) is None]
        if how == "any" and missing:
            continue
        if how == "all" and len(missing) == len(names):
            continue
        rows.append(row)
    return Table(table.columns, rows)


def rename_columns(table, mapping):
    unknown = set(mapping) - set(table.columns)
    if unknown:
        raise KeyError(f"unknown columns: {sorted(unknown)!r}")
    columns = [mapping.get(name, name) for name in table.columns]
    return Table(columns, table.rows)


def _resolve_columns(table, columns):
    if columns is None:
        return list(table.columns)
    names = list(columns)
    for name in names:
        table._check_column(name)
    return names
