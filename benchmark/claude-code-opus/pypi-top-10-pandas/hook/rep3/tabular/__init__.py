"""Load, clean and analyze tabular data from CSV files (standard library only).

Quick start::

    import tabular as tb

    t = tb.read_csv("sales.csv")
    t = tb.clean(t)
    print(tb.format_describe(tb.describe(t)))
    print(tb.group_by(t, "region", {"amount": ["sum", "mean"]}).to_dicts())
"""

from .analysis import (
    AGGREGATIONS,
    correlation,
    correlation_matrix,
    describe,
    format_describe,
    group_by,
    missing_report,
    numeric_columns,
    summarize_column,
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
    snake_case,
    strip_whitespace,
)
from .loader import DEFAULT_NA_VALUES, infer_type, read_csv, write_csv
from .table import Table

__all__ = [
    "AGGREGATIONS", "DEFAULT_NA_VALUES", "Table",
    "clean", "convert_types", "correlation", "correlation_matrix", "describe",
    "drop_duplicates", "drop_empty_columns", "drop_missing", "fill_missing",
    "format_describe", "group_by", "infer_type", "infer_types", "missing_report",
    "normalize_column_names", "numeric_columns", "read_csv", "remove_outliers",
    "snake_case", "strip_whitespace", "summarize_column", "value_counts", "write_csv",
]
