"""Functions to load CSV files into pandas DataFrames."""

import pandas as pd


def load_csv(path, **kwargs):
    """Load a CSV file into a DataFrame.

    Parameters
    ----------
    path : str
        Path to the CSV file.
    **kwargs :
        Additional keyword arguments passed to ``pd.read_csv``.

    Returns
    -------
    pd.DataFrame
    """
    return pd.read_csv(path, **kwargs)


def load_multiple_csv(paths, **kwargs):
    """Load and concatenate multiple CSV files into a single DataFrame.

    Parameters
    ----------
    paths : list[str]
        List of file paths to CSV files.
    **kwargs :
        Additional keyword arguments passed to ``pd.read_csv``.

    Returns
    -------
    pd.DataFrame
    """
    frames = [pd.read_csv(p, **kwargs) for p in paths]
    return pd.concat(frames, ignore_index=True)