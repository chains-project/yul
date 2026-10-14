"""tabular: a small, dependency-free library for loading, cleaning and
analyzing tabular data from CSV files.

Quick start::

    import tabular as tb

    table = tb.load_csv("sales.csv")
    table = tb.clean(table)
    table = tb.fill_missing(table, strategy="median", columns=["price"])
    print(tb.format_describe(tb.describe(table)))
    print(tb.group_by(table, "region", {"price": ["mean", "max"]}).to_dict())
"""

from .analysis import (
    AGGREGATORS,
    column_types,
    correlation,
    correlation_matrix,
    describe,
    format_describe,
    group_by,
    histogram,
    is_numeric,
    missing_report,
    numeric_columns,
    value_counts,
)
from .cleaning import (
    clean,
    convert_types,
    drop_duplicates,
    drop_empty_columns,
    drop_missing,
    fill_missing,
    infer_types,
    normalize_column_names,
    remove_outliers,
    replace_values,
    strip_whitespace,
)
from .io import DEFAULT_NA_VALUES, infer_column, load_csv, save_csv
from .table import Table

__all__ = [
    "AGGREGATORS", "DEFAULT_NA_VALUES", "Table",
    "clean", "column_types", "convert_types", "correlation", "correlation_matrix",
    "describe", "drop_duplicates", "drop_empty_columns", "drop_missing",
    "fill_missing", "format_describe", "group_by", "histogram", "infer_column",
    "infer_types", "is_numeric", "load_csv", "missing_report",
    "normalize_column_names", "numeric_columns", "remove_outliers",
    "replace_values", "save_csv", "strip_whitespace", "value_counts",
]
__version__ = "0.1.0"
