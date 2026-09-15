"""Load, clean, and analyze tabular data from CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path: str | Path, **read_csv_kwargs) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(path, **read_csv_kwargs)


def clean_data(
    df: pd.DataFrame,
    *,
    drop_duplicates: bool = True,
    dropna_how: str | None = "all",
) -> pd.DataFrame:
    """Return a cleaned copy of df: trimmed strings, deduped rows, empty rows removed."""
    cleaned = df.copy()

    cleaned.columns = [str(col).strip() for col in cleaned.columns]

    for col in cleaned.select_dtypes(include="object").columns:
        cleaned[col] = cleaned[col].str.strip()

    if dropna_how is not None:
        cleaned = cleaned.dropna(how=dropna_how)

    if drop_duplicates:
        cleaned = cleaned.drop_duplicates()

    return cleaned.reset_index(drop=True)


def analyze_data(df: pd.DataFrame) -> dict:
    """Return summary statistics for a DataFrame."""
    numeric_df = df.select_dtypes(include="number")
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "summary": numeric_df.describe().to_dict() if not numeric_df.empty else {},
    }


def load_and_analyze(path: str | Path, **read_csv_kwargs) -> dict:
    """Load a CSV, clean it, and return its summary statistics."""
    df = load_csv(path, **read_csv_kwargs)
    df = clean_data(df)
    return analyze_data(df)
