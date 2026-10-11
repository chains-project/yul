"""datalab: load, clean and analyze tabular data from CSV files.

The library is intentionally dependency-free and built on the standard
library.  A typical workflow looks like::

    import datalab as dl

    table = dl.load_csv("sales.csv")
    table = dl.strip_whitespace(table)
    table = dl.drop_duplicates(table)
    table = dl.fill_missing(table, strategy="median", columns=["amount"])
    print(dl.describe(table))
    print(dl.value_counts(table, "region"))
"""

from .analyze import (
    correlation,
    count,
    covariance,
    describe,
    group_by,
    mean,
    median,
    numeric_values,
    quantile,
    stdev,
    value_counts,
)
from .clean import (
    coerce_numeric,
    convert_types,
    drop_columns,
    drop_duplicates,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    rename_columns,
    replace_values,
    strip_whitespace,
)
from .load import load_csv, load_rows, make_unique_headers
from .table import Column, ColumnNotFoundError, Table, is_missing, to_number

__version__ = "0.1.0"

__all__ = [
    "Table",
    "Column",
    "ColumnNotFoundError",
    "load_csv",
    "load_rows",
    "make_unique_headers",
    "strip_whitespace",
    "drop_empty_rows",
    "drop_duplicates",
    "drop_missing",
    "fill_missing",
    "rename_columns",
    "drop_columns",
    "replace_values",
    "convert_types",
    "coerce_numeric",
    "count",
    "value_counts",
    "numeric_values",
    "mean",
    "median",
    "stdev",
    "quantile",
    "describe",
    "correlation",
    "covariance",
    "group_by",
    "is_missing",
    "to_number",
    "__version__",
]
