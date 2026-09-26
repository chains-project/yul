"""Load, clean, and analyze tabular data from CSV files."""

from pathlib import Path

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop empty rows/columns, strip whitespace from strings, and remove duplicates."""
    df = df.dropna(how="all").dropna(axis=1, how="all")
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df.drop_duplicates().reset_index(drop=True)


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """Return summary statistics for the numeric columns of a DataFrame."""
    return df.describe()


def load_and_analyze(path: str | Path) -> pd.DataFrame:
    """Convenience wrapper: load a CSV, clean it, and summarize it."""
    return analyze(clean(load_csv(path)))
