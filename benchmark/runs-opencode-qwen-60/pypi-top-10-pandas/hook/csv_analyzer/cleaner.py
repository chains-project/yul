import pandas as pd
import numpy as np
from typing import Optional, List, Union, Dict


def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None,
    keep: str = "first",
) -> pd.DataFrame:
    """Remove duplicate rows from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    subset : list, optional
        Column names to consider for identifying duplicates. Default is None (all columns).
    keep : {'first', 'last', False}, optional
        Which duplicate to keep. Default is 'first'.

    Returns
    -------
    pd.DataFrame
        DataFrame with duplicates removed.
    """
    before_count = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    after_count = len(df_clean)

    if before_count != after_count:
        print(f"Removed {before_count - after_count} duplicate rows.")

    return df_clean


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    fill_value: Optional[Union[int, float, str]] = None,
    columns: Optional[List[str]] = None,
    threshold: Optional[int] = None,
) -> pd.DataFrame:
    """Handle missing values in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    strategy : {'drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_value'}, optional
        Strategy for handling missing values. Default is 'drop'.
    fill_value : int, float, or str, optional
        Value to use when strategy is 'fill_value'.
    columns : list, optional
        Specific columns to apply the strategy to. Default is None (all columns).
    threshold : int, optional
        Drop rows with more than this many missing values (only for 'drop' strategy).

    Returns
    -------
    pd.DataFrame
        DataFrame with missing values handled.

    Raises
    ------
    ValueError
        If an invalid strategy is provided.
    """
    if columns:
        missing = df[columns].isnull().sum().sum()
    else:
        missing = df.isnull().sum().sum()

    if missing == 0:
        print("No missing values found.")
        return df

    print(f"Found {missing} missing values before cleaning.")

    if columns:
        df_clean = df.copy()
    else:
        df_clean = df.copy()

    if strategy == "drop":
        if threshold:
            df_clean = df_clean.dropna(threshold=threshold)
        else:
            df_clean = df_clean.dropna()
        print(f"Dropped rows with missing values. Remaining: {len(df_clean)} rows.")

    elif strategy == "fill_mean":
        numeric_cols = df_clean[columns].select_dtypes(include=[np.number]).columns if columns else df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if columns and col not in columns:
                continue
            mean_val = df_clean[col].mean()
            df_clean[col] = df_clean[col].fillna(mean_val)
        print(f"Filled numeric missing values with mean.")

    elif strategy == "fill_median":
        numeric_cols = df_clean[columns].select_dtypes(include=[np.number]).columns if columns else df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if columns and col not in columns:
                continue
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
        print(f"Filled numeric missing values with median.")

    elif strategy == "fill_mode":
        for col in df_clean.columns:
            if columns and col not in columns:
                continue
            mode_val = df_clean[col].mode()
            if not mode_val.empty:
                df_clean[col] = df_clean[col].fillna(mode_val[0])
        print(f"Filled missing values with mode.")

    elif strategy == "fill_value":
        if fill_value is None:
            raise ValueError("fill_value must be provided when strategy is 'fill_value'")
        if columns:
            df_clean[columns] = df_clean[columns].fillna(fill_value)
        else:
            df_clean = df_clean.fillna(fill_value)
        print(f"Filled missing values with: {fill_value}")

    else:
        raise ValueError(
            f"Invalid strategy: {strategy}. "
            "Choose from: 'drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_value'"
        )

    remaining_missing = df_clean.isnull().sum().sum()
    if remaining_missing > 0:
        print(f"Remaining missing values after cleaning: {remaining_missing}")

    return df_clean


def clean_column_names(
    df: pd.DataFrame,
    strategy: str = "lowercase",
) -> pd.DataFrame:
    """Clean and standardize column names.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    strategy : {'lowercase', 'uppercase', 'camelcase', 'snakecase'}, optional
        Strategy for cleaning column names. Default is 'lowercase'.

    Returns
    -------
    pd.DataFrame
        DataFrame with cleaned column names.
    """
    if strategy == "lowercase":
        df_clean = df.rename(columns=lambda x: str(x).lower().strip())
    elif strategy == "uppercase":
        df_clean = df.rename(columns=lambda x: str(x).upper().strip())
    elif strategy in ("camelcase", "snakecase"):
        import re

        def to_snake(name):
            name = re.sub(r"[\s\-_]+", "_", str(name))
            name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
            name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
            return name.lower().strip("_")

        df_clean = df.rename(columns=lambda x: to_snake(x))
    else:
        raise ValueError(
            f"Invalid strategy: {strategy}. "
            "Choose from: 'lowercase', 'uppercase', 'camelcase', 'snakecase'"
        )

    print(f"Column names cleaned using strategy: {strategy}")
    return df_clean


def remove_outliers_iqr(
    df: pd.DataFrame,
    columns: List[str],
    lower_bound: float = 1.5,
    upper_bound: float = 1.5,
) -> pd.DataFrame:
    """Remove outliers using the IQR method.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list
        List of numeric column names to check for outliers.
    lower_bound : float, optional
        Lower bound multiplier (Q1 - 1.5 * IQR). Default is 1.5.
    upper_bound : float, optional
        Upper bound multiplier (Q3 + 1.5 * IQR). Default is 1.5.

    Returns
    -------
    pd.DataFrame
        DataFrame with outliers removed.
    """
    df_clean = df.copy()
    rows_before = len(df_clean)

    for col in columns:
        if col not in df_clean.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")

        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - lower_bound * IQR
        upper = Q3 + upper_bound * IQR

        df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]

    rows_after = len(df_clean)
    if rows_before != rows_after:
        print(f"Removed {rows_before - rows_after} outlier rows from {len(columns)} columns.")

    return df_clean


def clean_csv(
    df: pd.DataFrame,
    remove_dupes: bool = True,
    handle_missing: str = "drop",
    clean_names: bool = True,
    fill_value: Optional[Union[int, float, str]] = None,
) -> pd.DataFrame:
    """Apply a full cleaning pipeline to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    remove_dupes : bool, optional
        Whether to remove duplicate rows. Default is True.
    handle_missing : {'drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_value'}, optional
        Strategy for handling missing values. Default is 'drop'.
    clean_names : bool, optional
        Whether to clean column names. Default is True.
    fill_value : int, float, or str, optional
        Value to use when handle_missing is 'fill_value'.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    print("Starting data cleaning pipeline...")

    if remove_dupes:
        df = remove_duplicates(df)

    if clean_names:
        df = clean_column_names(df)

    if handle_missing != "drop":
        df = handle_missing_values(df, strategy=handle_missing, fill_value=fill_value)
    else:
        df = handle_missing_values(df, strategy="drop")

    print("Data cleaning complete.")
    return df