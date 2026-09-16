import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Union


def describe_data(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    include: str = "all",
) -> pd.DataFrame:
    """Generate descriptive statistics for a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list, optional
        List of columns to describe. Default is None (all columns).
    include : {'all', 'numeric', 'categorical'}, optional
        Type of data to include in description. Default is 'all'.

    Returns
    -------
    pd.DataFrame
        Descriptive statistics.
    """
    if columns:
        df_subset = df[columns]
    else:
        df_subset = df.copy()

    print(f"Descriptive Statistics for {len(df_subset.columns)} columns:")
    print("=" * 60)

    if include in ("all", "numeric"):
        numeric_cols = df_subset.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print("\nNumeric Columns:")
            print("-" * 40)
            print(df_subset[numeric_cols].describe().round(2).to_string())

    if include in ("all", "categorical"):
        categorical_cols = df_subset.select_dtypes(exclude=[np.number]).columns
        if len(categorical_cols) > 0:
            print("\nCategorical Columns:")
            print("-" * 40)
            for col in categorical_cols:
                print(f"\n{col}:")
                print(f"  Unique values: {df_subset[col].nunique()}")
                print(f"  Most common:")
                print(df_subset[col].value_counts().head(5).to_string().replace("\n", "\n    "))

    print("\n" + "=" * 60)

    return df_subset.describe()


def get_column_summary(
    df: pd.DataFrame,
    column: str,
) -> Dict:
    """Get a detailed summary of a single column.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    column : str
        Column name to summarize.

    Returns
    -------
    dict
        Dictionary containing column summary statistics.

    Raises
    ------
    KeyError
        If the column does not exist in the DataFrame.
    """
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    summary = {
        "column": column,
        "dtype": str(df[column].dtype),
        "non_null_count": int(df[column].notna().sum()),
        "null_count": int(df[column].isna().sum()),
        "null_percentage": round(df[column].isna().mean() * 100, 2),
        "unique_count": int(df[column].nunique()),
    }

    if pd.api.types.is_numeric_dtype(df[column]):
        summary.update({
            "mean": round(df[column].mean(), 2),
            "std": round(df[column].std(), 2),
            "min": round(df[column].min(), 2),
            "max": round(df[column].max(), 2),
            "median": round(df[column].median(), 2),
        })
    else:
        summary.update({
            "most_common": df[column].value_counts().index[0],
            "most_common_count": int(df[column].value_counts().iloc[0]),
        })

    print(f"Column Summary: {column}")
    print("-" * 40)
    for key, value in summary.items():
        print(f"  {key}: {value}")

    return summary


def group_and_aggregate(
    df: pd.DataFrame,
    groupby: str,
    agg_dict: Dict[str, Union[str, List[str]]],
) -> pd.DataFrame:
    """Group data and apply aggregation functions.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    groupby : str
        Column name to group by.
    agg_dict : dict
        Dictionary mapping column names to aggregation functions.
        Example: {'salary': ['mean', 'sum'], 'age': 'median'}

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame.

    Raises
    ------
    KeyError
        If specified columns do not exist in the DataFrame.
    """
    if groupby not in df.columns:
        raise KeyError(f"Groupby column '{groupby}' not found in DataFrame.")

    for col in agg_dict.keys():
        if col not in df.columns:
            raise KeyError(f"Aggregation column '{col}' not found in DataFrame.")

    result = df.groupby(groupby).agg(agg_dict)
    result.columns = ["_".join(col).strip() if isinstance(col, tuple) else col for col in result.columns]
    result = result.reset_index()

    print(f"Grouped by '{groupby}' and aggregated.")
    print(result.to_string(index=False))

    return result


def cross_tabulate(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    values: Optional[str] = None,
    aggfunc: Optional[str] = None,
    margins: bool = False,
) -> pd.DataFrame:
    """Create a cross-tabulation (contingency table) of two columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    col1 : str
        First column name.
    col2 : str
        Second column name.
    values : str, optional
        Column to aggregate (requires aggfunc).
    aggfunc : str, optional
        Aggregation function when values is specified (e.g., 'mean', 'sum', 'count').
    margins : bool, optional
        Add row/column margins (subtotals). Default is False.

    Returns
    -------
    pd.DataFrame
        Cross-tabulation DataFrame.
    """
    for col in [col1, col2]:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame.")

    if values and aggfunc:
        result = pd.crosstab(
            index=df[col1],
            columns=df[col2],
            values=df[values],
            aggfunc=aggfunc,
            margins=margins,
        )
    else:
        result = pd.crosstab(
            index=df[col1],
            columns=df[col2],
            margins=margins,
        )

    print(f"Cross-tabulation of '{col1}' vs '{col2}':")
    print(result.to_string())

    return result


def filter_data(
    df: pd.DataFrame,
    conditions: Dict[str, Union[int, float, str, tuple]],
) -> pd.DataFrame:
    """Filter DataFrame based on column conditions.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    conditions : dict
        Dictionary mapping column names to filter conditions.
        For numeric: {'column': ('min', 'max')} or {'column': value}
        For categorical: {'column': ['value1', 'value2']} or {'column': 'value'}

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.

    Example
    -------
    >>> filter_data(df, {'age': (18, 65), 'city': ['NYC', 'LA']})
    """
    mask = pd.Series([True] * len(df), index=df.index)
    conditions_met = []

    for col, condition in conditions.items():
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame.")

        if isinstance(condition, tuple) and len(condition) == 2:
            mask &= (df[col] >= condition[0]) & (df[col] <= condition[1])
            conditions_met.append(f"{col} between {condition[0]} and {condition[1]}")
        elif isinstance(condition, list):
            mask &= df[col].isin(condition)
            conditions_met.append(f"{col} in {condition}")
        else:
            mask &= (df[col] == condition)
            conditions_met.append(f"{col} == {condition}")

    result = df[mask]
    print(f"Filtered {len(df)} rows to {len(result)} rows using conditions: {', '.join(conditions_met)}")

    return result


def export_data(
    df: pd.DataFrame,
    output_path: str,
    index: bool = False,
    **kwargs,
) -> str:
    """Export DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to export.
    output_path : str
        Path for the output CSV file.
    index : bool, optional
        Whether to write row indices. Default is False.
    **kwargs
        Additional keyword arguments passed to DataFrame.to_csv().

    Returns
    -------
    str
        Path to the exported file.
    """
    df.to_csv(output_path, index=index, **kwargs)
    print(f"Exported {len(df)} rows to {output_path}")
    return output_path