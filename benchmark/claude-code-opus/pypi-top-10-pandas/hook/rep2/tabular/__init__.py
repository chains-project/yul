"""Load, clean, and analyze tabular data from CSV files.

Example:
    >>> from tabular import clean, describe, load_csv
    >>> table = clean(load_csv("sales.csv"))
    >>> print(describe(table).to_string())
"""

from tabular.analysis import correlation, describe, group_by, value_counts
from tabular.cleaning import (
    clean,
    drop_duplicates,
    drop_empty_columns,
    drop_missing,
    fill_missing,
    normalize_column_names,
    strip_whitespace,
)
from tabular.io import load_csv, save_csv
from tabular.table import Table

__all__ = [
    "Table",
    "clean",
    "correlation",
    "describe",
    "drop_duplicates",
    "drop_empty_columns",
    "drop_missing",
    "fill_missing",
    "group_by",
    "load_csv",
    "normalize_column_names",
    "save_csv",
    "strip_whitespace",
    "value_counts",
]
