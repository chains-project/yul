"""Load, clean, and analyze tabular data from CSV files."""

import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    """Read a CSV file into a DataFrame."""
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop empty rows/columns, remove duplicates, and strip whitespace from string columns."""
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df = df.drop_duplicates()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df.reset_index(drop=True)


def analyze_data(df: pd.DataFrame) -> dict:
    """Return summary statistics for a DataFrame."""
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "missing_values": df.isna().sum().to_dict(),
        "numeric_summary": df.describe(include="number").to_dict(),
    }


def load_and_analyze(path: str) -> dict:
    """Load a CSV file, clean it, and return its summary statistics."""
    df = clean_data(load_csv(path))
    return analyze_data(df)
