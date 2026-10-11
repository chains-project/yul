"""tabular: load, clean and analyze CSV data with the standard library.

Example
-------
>>> from tabular import read_csv, drop_missing, convert_types, describe
>>> table = read_csv("data.csv")                     # doctest: +SKIP
>>> table = drop_missing(table, how="any")           # doctest: +SKIP
>>> table = convert_types(table, {"price": "float"}) # doctest: +SKIP
>>> print(describe(table))                           # doctest: +SKIP
"""

from .analysis import (
    correlation,
    describe,
    group_by,
    maximum,
    mean,
    median,
    minimum,
    numeric_values,
    quantile,
    stdev,
    summary,
    total,
    value_counts,
    variance,
)
from .clean import (
    convert_types,
    drop_duplicates,
    drop_missing,
    fill_missing,
    filter_rows,
    normalize_column_names,
    replace_values,
    strip_whitespace,
)
from .io import (
    DEFAULT_MISSING,
    coerce_value,
    infer_value,
    read_csv,
    read_csv_string,
    write_csv,
)
from .table import Table

__version__ = "0.1.0"

__all__ = [
    "Table",
    "read_csv",
    "read_csv_string",
    "write_csv",
    "infer_value",
    "coerce_value",
    "DEFAULT_MISSING",
    "strip_whitespace",
    "normalize_column_names",
    "drop_missing",
    "fill_missing",
    "drop_duplicates",
    "convert_types",
    "replace_values",
    "filter_rows",
    "mean",
    "median",
    "variance",
    "stdev",
    "minimum",
    "maximum",
    "total",
    "quantile",
    "numeric_values",
    "value_counts",
    "correlation",
    "summary",
    "describe",
    "group_by",
    "__version__",
]
