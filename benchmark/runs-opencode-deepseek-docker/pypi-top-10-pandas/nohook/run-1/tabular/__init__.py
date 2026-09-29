r"""A small, dependency-free toolkit for loading, cleaning and analysing CSV data.

Example
-------
>>> from tabular import load_csv_string
>>> table = load_csv_string("name,age\nAda,36\nGrace,\n")
>>> table.convert_types().drop_missing().mean("age")
36.0
"""

from __future__ import annotations

from .errors import ColumnNotFoundError, CSVLoadError, TabularError
from .io import load_csv, load_csv_string
from .table import DataTable

__version__ = "0.1.0"

__all__ = [
    "DataTable",
    "load_csv",
    "load_csv_string",
    "TabularError",
    "CSVLoadError",
    "ColumnNotFoundError",
]
