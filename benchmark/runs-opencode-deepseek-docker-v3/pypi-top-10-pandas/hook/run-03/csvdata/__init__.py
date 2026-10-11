"""csvdata: load, clean, and analyze tabular data from CSV files.

Example
-------
>>> from csvdata import load_csv, coerce_types, drop_missing, describe
>>> table = coerce_types(drop_missing(load_csv("data.csv")))
>>> describe(table)["price"]["mean"]
"""

from .analyze import column_summary, correlation, describe, value_counts
from .clean import (
    coerce_types,
    drop_duplicates,
    drop_missing,
    fill_missing,
    normalize_headers,
    strip_whitespace,
)
from .loaders import load_csv, read_csv
from .table import Table, is_missing

__all__ = [
    "Table",
    "is_missing",
    "load_csv",
    "read_csv",
    "strip_whitespace",
    "normalize_headers",
    "coerce_types",
    "drop_missing",
    "fill_missing",
    "drop_duplicates",
    "column_summary",
    "describe",
    "value_counts",
    "correlation",
]

__version__ = "0.1.0"
