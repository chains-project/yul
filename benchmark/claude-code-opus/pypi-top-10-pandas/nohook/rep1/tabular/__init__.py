"""Load, clean, and analyze tabular data from CSV files.

Pure standard library; no third-party dependencies.

    >>> from tabular import load_csv
    >>> t = load_csv("sales.csv").clean_column_names().drop_duplicates()
    >>> t.describe()["price"]["mean"]
"""

from .table import Table
from .loader import load_csv, read_csv_text, write_csv
from .clean import (
    clean_column_names,
    strip_whitespace,
    drop_duplicates,
    drop_missing,
    fill_missing,
    cast_column,
    filter_rows,
)
from .analysis import describe, value_counts, correlation, group_by

__all__ = [
    "Table",
    "load_csv",
    "read_csv_text",
    "write_csv",
    "clean_column_names",
    "strip_whitespace",
    "drop_duplicates",
    "drop_missing",
    "fill_missing",
    "cast_column",
    "filter_rows",
    "describe",
    "value_counts",
    "correlation",
    "group_by",
]
