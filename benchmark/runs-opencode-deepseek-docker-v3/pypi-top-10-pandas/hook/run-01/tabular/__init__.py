"""tabular: load, clean, and analyze tabular data from CSV files.

Built entirely on the Python standard library (no third-party dependencies).

Quick start::

    import tabular as tb

    table = tb.load_csv("data.csv")
    table = tb.drop_duplicates(tb.drop_missing(table))
    stats = tb.describe(table)
    print(tb.value_counts(table, "region", top=5))
"""

from .analyzer import (
    ColumnStats,
    aggregate,
    column_type,
    column_types,
    correlation,
    describe,
    group_by,
    value_counts,
)
from .cleaner import (
    cast_column,
    coerce_column,
    drop_duplicates,
    drop_empty_columns,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    normalize_headers,
    rename_columns,
    replace_values,
    strip_whitespace,
)
from .loader import infer_type, load_csv, load_rows
from .table import Table

__version__ = "0.1.0"

__all__ = [
    "Table",
    "ColumnStats",
    "load_csv",
    "load_rows",
    "infer_type",
    "normalize_headers",
    "strip_whitespace",
    "replace_values",
    "fill_missing",
    "drop_missing",
    "drop_empty_rows",
    "drop_empty_columns",
    "drop_duplicates",
    "cast_column",
    "coerce_column",
    "rename_columns",
    "describe",
    "column_type",
    "column_types",
    "value_counts",
    "correlation",
    "group_by",
    "aggregate",
]
