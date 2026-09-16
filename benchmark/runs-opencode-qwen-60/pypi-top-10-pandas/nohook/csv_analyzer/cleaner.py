"""Functions to clean and preprocess tabular data."""

import pandas as pd


def drop_missing(df, columns=None):
    """Remove rows with missing values.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str] | None, optional
        Subset of columns to check for missing values. If ``None``,
        all columns are checked.

    Returns
    -------
    pd.DataFrame
    """
    if columns:
        return df.dropna(subset=columns).reset_index(drop=True)
    return df.dropna().reset_index(drop=True)


def fill_missing(df, strategy="mean", columns=None, fill_value=None):
    """Fill missing values using the specified strategy.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    strategy : str, default ``"mean"``
        One of ``"mean"``, ``"median"``, ``"mode"``, or ``"value"``.
        When ``"value"`` is used, ``fill_value`` must also be provided.
    columns : list[str] | None, optional
        Subset of columns to fill. If ``None``, all columns are filled.
    fill_value : optional
        Literal value to use when ``strategy="value"``.

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    cols = columns if columns else df.columns.tolist()
    cols = [c for c in cols if c in df.columns]

    if strategy == "mean":
        for c in cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].fillna(df[c].mean())
    elif strategy == "median":
        for c in cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].fillna(df[c].median())
    elif strategy == "mode":
        for c in cols:
            mode_val = df[c].mode()
            if len(mode_val) > 0:
                df[c] = df[c].fillna(mode_val[0])
    elif strategy == "value":
        df[cols] = df[cols].fillna(fill_value)

    return df.reset_index(drop=True)


def remove_duplicates(df, subset=None):
    """Remove duplicate rows.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    subset : list[str] | None, optional
        Columns to consider for identifying duplicates.

    Returns
    -------
    pd.DataFrame
    """
    return df.drop_duplicates(subset=subset).reset_index(drop=True)


def remove_outliers_iqr(df, columns, lower_bound=1.5):
    """Remove rows where specified numeric columns fall outside IQR-based bounds.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str]
        Numeric columns to check.
    lower_bound : float, default 1.5
        Multiplier for the IQR (used for both upper and lower fences).

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    mask = pd.Series(True, index=df.index)
    for c in columns:
        if c not in df.columns:
            continue
        q1 = df[c].quantile(0.25)
        q3 = df[c].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - lower_bound * iqr
        upper = q3 + lower_bound * iqr
        mask &= df[c].between(lower, upper, inclusive="both")
    return df.loc[mask].reset_index(drop=True)


def convert_dtype(df, col_type_map):
    """Convert columns to specified dtypes.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    col_type_map : dict[str, str]
        Mapping of column names to target dtype strings (e.g. ``{"age": int, "name": str}``).

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    for col, dtype in col_type_map.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    return df


def clean(
    df,
    drop_na=False,
    fill_na_strategy="mean",
    fill_na_columns=None,
    remove_dups=False,
    remove_outlier_cols=None,
    remove_outlier_bound=1.5,
    col_type_map=None,
):
    """Convenience wrapper that applies a standard cleaning pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    drop_na : bool, default ``False``
        Whether to drop rows with any missing value.
    fill_na_strategy : str, default ``"mean"``
        Strategy for imputing missing numeric values.
    fill_na_columns : list[str] | None, optional
        Columns to impute.
    remove_dups : bool, default ``False``
        Whether to remove duplicate rows.
    remove_outlier_cols : list[str] | None, optional
        Numeric columns to check for outliers (IQR method).
    remove_outlier_bound : float, default 1.5
        IQR multiplier for outlier detection.
    col_type_map : dict[str, str] | None, optional
        Column-to-dtype conversions.

    Returns
    -------
    pd.DataFrame
    """
    if drop_na:
        df = drop_missing(df)
    df = fill_missing(df, strategy=fill_na_strategy, columns=fill_na_columns)
    if remove_dups:
        df = remove_duplicates(df)
    if remove_outlier_cols:
        df = remove_outliers_iqr(df, columns=remove_outlier_cols, lower_bound=remove_outlier_bound)
    if col_type_map:
        df = convert_dtype(df, col_type_map)
    return df.reset_index(drop=True)