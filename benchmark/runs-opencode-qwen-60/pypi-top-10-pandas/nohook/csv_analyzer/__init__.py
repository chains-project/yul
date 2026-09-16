"""Library for loading, cleaning, and analyzing tabular data from CSV files."""

from csv_analyzer.analyzer import (
    analyze,
    column_counts,
    correlations,
    describe,
    group_summary,
    summary,
)
from csv_analyzer.cleaner import (
    clean,
    convert_dtype,
    drop_missing,
    fill_missing,
    remove_duplicates,
    remove_outliers_iqr,
)
from csv_analyzer.loader import load_csv, load_multiple_csv

__all__ = [
    "load_csv",
    "load_multiple_csv",
    "drop_missing",
    "fill_missing",
    "remove_duplicates",
    "remove_outliers_iqr",
    "convert_dtype",
    "clean",
    "describe",
    "summary",
    "correlations",
    "column_counts",
    "group_summary",
    "analyze",
]