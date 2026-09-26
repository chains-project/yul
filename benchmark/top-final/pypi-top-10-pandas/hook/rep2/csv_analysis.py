"""Load, clean, and analyze tabular data from CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop empty rows/columns, remove duplicates, and strip whitespace from string columns."""
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df = df.drop_duplicates()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df.reset_index(drop=True)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    return df.describe(include="number")


def analyze_csv(path: str | Path) -> pd.DataFrame:
    """Load, clean, and summarize a CSV file in one call."""
    return summarize(clean(load_csv(path)))
