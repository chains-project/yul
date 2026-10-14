"""Load, clean, and analyze tabular data from CSV files.

Example::

    from tabular import load_csv

    table = load_csv("sales.csv").clean()
    print(table.describe())
    print(table.group_by("region", {"revenue": "sum"}))
"""

from .table import Table
from .loader import load_csv, read_csv_text
from .cleaning import MISSING_TOKENS, infer_type, normalize_name, parse_value

__all__ = [
    "Table",
    "load_csv",
    "read_csv_text",
    "MISSING_TOKENS",
    "infer_type",
    "normalize_name",
    "parse_value",
]
