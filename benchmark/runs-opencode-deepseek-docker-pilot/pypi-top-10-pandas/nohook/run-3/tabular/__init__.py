"""A small, dependency-free library for loading, cleaning and analyzing
tabular data from CSV files.

Typical use::

    from tabular import load_csv, replace_missing, coerce_numeric, describe

    table = load_csv("sales.csv")
    table = replace_missing(table)
    table = coerce_numeric(table)
    print(describe(table))
"""

from .analysis import (
    correlation,
    describe,
    infer_types,
    missing_report,
    numeric_summary,
    to_number,
    value_counts,
)
from .cleaning import (
    DEFAULT_MISSING,
    coerce_numeric,
    drop_duplicates,
    drop_empty_columns,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    is_missing,
    replace_missing,
    standardize_headers,
    strip_whitespace,
)
from .loaders import load_csv, load_csvs, write_csv
from .table import Table

__all__ = [
    "DEFAULT_MISSING",
    "Table",
    "coerce_numeric",
    "correlation",
    "describe",
    "drop_duplicates",
    "drop_empty_columns",
    "drop_empty_rows",
    "drop_missing",
    "fill_missing",
    "infer_types",
    "is_missing",
    "load_csv",
    "load_csvs",
    "missing_report",
    "numeric_summary",
    "replace_missing",
    "standardize_headers",
    "strip_whitespace",
    "to_number",
    "value_counts",
    "write_csv",
]

__version__ = "0.1.0"
