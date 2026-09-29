"""datalib: load, clean and analyze tabular data from CSV files.

The public API is intentionally small and works on a lightweight, dependency
free :class:`~datalib.table.Table`::

    import datalib

    table = datalib.load_csv("data.csv", infer_types=True)
    table = datalib.clean(table, drop_dupes=True, fill_strategy="mean")
    print(datalib.describe(table))

Submodules :mod:`datalib.loader`, :mod:`datalib.cleaning` and
:mod:`datalib.analysis` expose the full set of operations.
"""

from __future__ import annotations

from . import analysis, cleaning, loader
from .analysis import (
    correlation,
    correlation_matrix,
    describe,
    group_by,
    mean,
    median,
    value_counts,
)
from .cleaning import clean, coerce_types, drop_duplicates, drop_missing, fill_missing
from .exceptions import (
    CSVParseError,
    DataLibError,
    MissingColumnError,
    SchemaError,
)
from .loader import load_csv, load_csv_string, load_csvs
from .table import Table

__version__ = "0.1.0"

__all__ = [
    "Table",
    "load_csv",
    "load_csvs",
    "load_csv_string",
    "clean",
    "coerce_types",
    "drop_duplicates",
    "drop_missing",
    "fill_missing",
    "describe",
    "group_by",
    "value_counts",
    "correlation",
    "correlation_matrix",
    "mean",
    "median",
    "DataLibError",
    "MissingColumnError",
    "CSVParseError",
    "SchemaError",
    "loader",
    "cleaning",
    "analysis",
    "__version__",
]
