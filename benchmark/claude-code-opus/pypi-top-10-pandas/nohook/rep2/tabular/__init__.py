"""tabular: load, clean and analyze tabular data from CSV files.

Pure standard library; no third-party dependencies.

    >>> from tabular import load_csv, clean, analyze
    >>> t = load_csv("sales.csv")
    >>> t = clean.normalize_column_names(t)
    >>> t = clean.drop_duplicates(clean.strip_whitespace(t))
    >>> print(analyze.format_table(analyze.describe(t)))
"""

from . import analyze, clean
from .analyze import correlation, correlation_matrix, describe, format_table, group_by, missing_report, value_counts
from .io import load_csv, loads_csv, save_csv
from .table import Table

__all__ = [
    "Table",
    "analyze",
    "clean",
    "correlation",
    "correlation_matrix",
    "describe",
    "format_table",
    "group_by",
    "load_csv",
    "loads_csv",
    "missing_report",
    "save_csv",
    "value_counts",
]
