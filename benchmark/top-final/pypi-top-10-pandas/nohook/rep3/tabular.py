"""Load, clean, and analyze tabular data from CSV files."""

from __future__ import annotations

import pandas as pd


def load_csv(path: str, **kwargs) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(path, **kwargs)


def clean(df: pd.DataFrame, *, dedupe: bool = True) -> pd.DataFrame:
    """Trim whitespace from string columns, drop empty rows, and optionally dedupe."""
    df = df.dropna(how="all")
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    if dedupe:
        df = df.drop_duplicates()
    return df.reset_index(drop=True)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    return df.describe()


def analyze_csv(path: str, **read_kwargs) -> pd.DataFrame:
    """Load, clean, and summarize a CSV file in one call."""
    return summarize(clean(load_csv(path, **read_kwargs)))
