"""csvlab: load, clean, and analyze tabular data from CSV files."""

from .table import Table
from . import analysis, cleaners

__all__ = [
    "Table",
    "analysis",
    "cleaners",
]

__version__ = "0.1.0"
