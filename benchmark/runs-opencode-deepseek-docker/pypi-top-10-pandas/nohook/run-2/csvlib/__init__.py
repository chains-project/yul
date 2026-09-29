"""csvlib: load, clean and analyze tabular data from CSV files.

csvlib is a small, dependency-free toolkit built on the Python standard
library.  The central object is :class:`~csvlib.table.Table`, a column-oriented
table of values where ``None`` represents a missing cell.

Typical usage::

    import csvlib

    table = csvlib.load_csv("data.csv")
    table = csvlib.strip_whitespace(table)
    table = csvlib.coerce_types(table)
    print(csvlib.describe(table))
"""

from . import analyze, clean
from .analyze import (
    categorical_columns,
    column_stats,
    correlation,
    describe,
    group_by,
    is_numeric_column,
    missing_report,
    numeric_columns,
    summary,
    value_counts,
)
from .clean import (
    coerce_types,
    convert_column,
    drop_duplicates,
    drop_empty_columns,
    drop_empty_rows,
    drop_missing_columns,
    drop_missing_rows,
    fill_missing,
    filter_rows,
    normalize_columns,
    rename_columns,
    replace_values,
    select_columns,
    strip_whitespace,
)
from .loaders import DEFAULT_MISSING, load_csv, load_csvs, parse_csv
from .table import Table

__version__ = "0.1.0"

__all__ = [
    "Table",
    # loading
    "load_csv",
    "load_csvs",
    "parse_csv",
    "DEFAULT_MISSING",
    # cleaning
    "strip_whitespace",
    "replace_values",
    "fill_missing",
    "drop_empty_rows",
    "drop_empty_columns",
    "drop_missing_rows",
    "drop_missing_columns",
    "drop_duplicates",
    "filter_rows",
    "select_columns",
    "rename_columns",
    "normalize_columns",
    "convert_column",
    "coerce_types",
    # analysis
    "missing_report",
    "numeric_columns",
    "categorical_columns",
    "is_numeric_column",
    "value_counts",
    "column_stats",
    "describe",
    "summary",
    "correlation",
    "group_by",
    # submodules
    "clean",
    "analyze",
    "__version__",
]
