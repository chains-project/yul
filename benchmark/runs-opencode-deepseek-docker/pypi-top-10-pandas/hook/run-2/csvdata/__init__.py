"""A small, dependency-free toolkit for loading, cleaning and analyzing CSV data."""

from .analysis import (
    aggregate,
    correlation,
    describe,
    effective_dtypes,
    numeric_columns,
    summary,
    value_counts,
)
from .cleaning import (
    FILL_STRATEGIES,
    clean,
    coerce_types,
    drop_duplicates,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    infer_dtype,
    strip_whitespace,
)
from .errors import (
    AnalysisError,
    CleaningError,
    ColumnNotFoundError,
    CsvDataError,
    CsvLoadError,
)
from .loading import load_csv, load_csvs
from .render import format_record, format_table
from .table import Table

__version__ = "0.1.0"

__all__ = [
    "AnalysisError",
    "CleaningError",
    "ColumnNotFoundError",
    "CsvDataError",
    "CsvLoadError",
    "FILL_STRATEGIES",
    "Table",
    "__version__",
    "aggregate",
    "clean",
    "coerce_types",
    "correlation",
    "describe",
    "drop_duplicates",
    "drop_empty_rows",
    "drop_missing",
    "effective_dtypes",
    "fill_missing",
    "format_record",
    "format_table",
    "infer_dtype",
    "load_csv",
    "load_csvs",
    "numeric_columns",
    "strip_whitespace",
    "summary",
    "value_counts",
]
