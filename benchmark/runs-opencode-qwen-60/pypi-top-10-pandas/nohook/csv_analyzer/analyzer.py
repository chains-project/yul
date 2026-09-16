"""Functions for analyzing tabular data (descriptive statistics, correlations, distributions)."""

import pandas as pd


def describe(df, columns=None):
    """Return descriptive statistics for numeric columns (or a subset).

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str] | None, optional
        Subset of columns to include.

    Returns
    -------
    pd.DataFrame
    """
    if columns:
        df = df[columns]
    return df.describe()


def summary(df, columns=None):
    """Return a richer summary: numeric stats, unique counts, dtype, and missing-counts.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str] | None, optional
        Subset of columns to include.

    Returns
    -------
    pd.DataFrame
    """
    cols = columns if columns else df.columns.tolist()
    cols = [c for c in cols if c in df.columns]

    records = []
    for c in cols:
        col = df[c]
        rec = {
            "column": c,
            "dtype": str(col.dtype),
            "null_count": int(col.isna().sum()),
            "null_pct": round(col.isna().mean() * 100, 2),
            "unique_count": int(col.nunique()),
        }
        if pd.api.types.is_numeric_dtype(col):
            rec["mean"] = round(col.mean(), 4)
            rec["std"] = round(col.std(), 4)
            rec["min"] = round(col.min(), 4)
            rec["max"] = round(col.max(), 4)
        records.append(rec)

    return pd.DataFrame(records)


def correlations(df, method="pearson"):
    """Compute a correlation matrix for numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    method : str, default ``"pearson"``
        One of ``"pearson"``, ``"spearman"``, or ``"kendall"``.

    Returns
    -------
    pd.DataFrame
        Symmetric correlation matrix.
    """
    return df.corr(method=method)


def column_counts(df, columns=None, top_n=10):
    """Return the top-*n* most frequent values for categorical or object columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str] | None, optional
        Columns to inspect. If ``None``, all non-numeric columns are used.
    top_n : int, default 10
        Number of top values per column.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns ``["column", "value", "count", "pct"]``.
    """
    cols = columns if columns else df.select_dtypes(exclude="number").columns.tolist()
    rows = []
    for c in cols:
        counts = df[c].value_counts().head(top_n)
        total = len(df)
        for val, cnt in counts.items():
            rows.append({"column": c, "value": val, "count": int(cnt), "pct": round(cnt / total * 100, 2)})
    return pd.DataFrame(rows)


def group_summary(df, group_by, agg_dict):
    """Aggregate numeric columns by groups.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    group_by : str
        Column to group by.
    agg_dict : dict[str, str | list[str]]
        Mapping of target columns to aggregation function(s).

    Returns
    -------
    pd.DataFrame
    """
    return df.groupby(group_by, dropna=False).agg(agg_dict).reset_index()


def analyze(df):
    """Produce a full analysis report as a dictionary.

    Keys in the returned dict:
        - ``"info"``: basic shape / column overview
        - ``"summary"``: column-level summary DataFrame
        - ``"describe"``: ``df.describe()`` DataFrame
        - ``"correlations"``: correlation matrix (only when >= 2 numeric cols)
        - ``"missing"``: per-column null counts and percentages

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    dict
    """
    report = {}

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    report["info"] = {
        "shape": list(df.shape),
        "columns": df.columns.tolist(),
        "numeric_columns": numeric_cols,
        "object_columns": df.select_dtypes(exclude="number").columns.tolist(),
    }

    report["missing"] = {
        "column": df.columns,
        "null_count": df.isna().sum().values,
        "null_pct": (df.isna().mean() * 100).round(2).values,
    }

    report["summary"] = summary(df)
    report["describe"] = describe(df)

    if len(numeric_cols) >= 2:
        report["correlations"] = correlations(df[numeric_cols])
    else:
        report["correlations"] = None

    return report