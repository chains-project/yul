import pandas as pd
from typing import Optional, List, Dict, Union


def load_csv(
    filepath: str,
    encoding: Optional[str] = None,
    delimiter: Optional[str] = None,
    usecols: Optional[List[str]] = None,
    parse_dates: Optional[List[str]] = None,
    dtype: Optional[Dict[str, str]] = None,
    skiprows: Optional[Union[int, List[int]]] = None,
    na_values: Optional[List[str]] = None,
    header: Optional[int] = 0,
    index_col: Optional[Union[str, int]] = None,
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    encoding : str, optional
        File encoding (e.g., 'utf-8', 'latin-1'). Defaults to None (auto-detect).
    delimiter : str, optional
        Column separator. If None, pandas will auto-detect.
    usecols : list, optional
        List of column names to load.
    parse_dates : list, optional
        List of column names to parse as datetime.
    dtype : dict, optional
        Column names mapped to desired dtypes (e.g., {'age': 'int64'}).
    skiprows : int or list, optional
        Number of rows to skip from the top, or a list of row indices.
    na_values : list, optional
        Additional strings to recognize as NaN.
    header : int, optional
        Row number(s) to use as column names. Default is 0.
    index_col : str or int, optional
        Column to use as row labels.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is empty or cannot be parsed.
    KeyError
        If specified column names do not exist in the file.
    """
    kwargs = {
        "encoding": encoding,
        "delimiter": delimiter,
        "usecols": usecols,
        "parse_dates": parse_dates,
        "dtype": dtype,
        "skiprows": skiprows,
        "na_values": na_values,
        "header": header,
        "index_col": index_col,
    }

    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    try:
        df = pd.read_csv(filepath, **kwargs)
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse CSV file: {e}")

    if df.empty:
        raise ValueError(f"CSV file is empty or contains no parsable data: {filepath}")

    return df


def load_multiple_csv(
    filepaths: List[str],
    encoding: Optional[str] = None,
    delimiter: Optional[str] = None,
    ignore_errors: bool = False,
) -> List[pd.DataFrame]:
    """Load multiple CSV files into separate DataFrames.

    Parameters
    ----------
    filepaths : list
        List of file paths to CSV files.
    encoding : str, optional
        File encoding for all files.
    delimiter : str, optional
        Column separator for all files.
    ignore_errors : bool, optional
        If True, skip files that fail to load and continue. If False, raise on first error.

    Returns
    -------
    list
        List of DataFrames, one for each successfully loaded file.

    Raises
    ------
    FileNotFoundError
        If any file does not exist (when ignore_errors=False).
    ValueError
        If no files could be loaded.
    """
    dataframes = []
    errors = []

    for filepath in filepaths:
        try:
            df = load_csv(filepath, encoding=encoding, delimiter=delimiter)
            dataframes.append(df)
        except Exception as e:
            errors.append((filepath, str(e)))
            if not ignore_errors:
                raise

    if not dataframes:
        raise ValueError(
            f"No files could be loaded. Errors:\n" + "\n".join(
                f"  {fp}: {err}" for fp, err in errors
            )
        )

    return dataframes


def load_csv_with_preview(
    filepath: str,
    preview_rows: int = 5,
    **kwargs,
) -> pd.DataFrame:
    """Load a CSV file and display a preview of the data.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    preview_rows : int, optional
        Number of rows to display as a preview. Default is 5.
    **kwargs
        Additional keyword arguments passed to load_csv().

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.
    """
    df = load_csv(filepath, **kwargs)

    print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")
    print(f"Columns: {list(df.columns)}")
    print(f"\nPreview (first {preview_rows} rows):")
    print(df.head(preview_rows).to_string(index=False))
    print(f"\nData types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")

    return df