"""csv_analyzer - A library for loading, cleaning, and analyzing tabular data from CSV files.

This package provides utilities for:
    - Loading CSV files with various options
    - Cleaning data (removing duplicates, handling missing values, etc.)
    - Analyzing data (descriptive statistics, aggregation, filtering, etc.)

Example usage:
    >>> from csv_analyzer import CSVAnalyzer
    >>> analyzer = CSVAnalyzer()
    >>> df = analyzer.load("data.csv")
    >>> df = analyzer.clean(df)
    >>> analyzer.describe(df)
    >>> analyzer.export(df, "cleaned_data.csv")
"""

from csv_analyzer.loader import load_csv, load_multiple_csv, load_csv_with_preview
from csv_analyzer.cleaner import (
    remove_duplicates,
    handle_missing_values,
    clean_column_names,
    remove_outliers_iqr,
    clean_csv,
)
from csv_analyzer.analyzer import (
    describe_data,
    get_column_summary,
    group_and_aggregate,
    cross_tabulate,
    filter_data,
    export_data,
)


class CSVAnalyzer:
    """Main class for loading, cleaning, and analyzing CSV data.

    This class provides a convenient interface for performing common
    data analysis tasks on CSV files.

    Example
    -------
    >>> analyzer = CSVAnalyzer()
    >>> df = analyzer.load("data.csv")
    >>> df = analyzer.clean(df)
    >>> analyzer.describe(df)
    >>> analyzer.export(df, "cleaned_data.csv")
    """

    def load(
        self,
        filepath: str,
        encoding = None,
        delimiter = None,
        usecols = None,
        parse_dates = None,
        dtype = None,
        skiprows = None,
        na_values = None,
        header = 0,
        index_col = None,
    ):
        """Load a CSV file into a DataFrame.

        Parameters
        ----------
        filepath : str
            Path to the CSV file.
        encoding : str, optional
            File encoding.
        delimiter : str, optional
            Column separator.
        usecols : list, optional
            List of column names to load.
        parse_dates : list, optional
            List of column names to parse as datetime.
        dtype : dict, optional
            Column dtypes.
        skiprows : int or list, optional
            Rows to skip.
        na_values : list, optional
            Additional NaN values.
        header : int, optional
            Row number(s) to use as column names.
        index_col : str or int, optional
            Column to use as row labels.

        Returns
        -------
        pd.DataFrame
            Loaded DataFrame.
        """
        return load_csv(
            filepath=filepath,
            encoding=encoding,
            delimiter=delimiter,
            usecols=usecols,
            parse_dates=parse_dates,
            dtype=dtype,
            skiprows=skiprows,
            na_values=na_values,
            header=header,
            index_col=index_col,
        )

    def load_multiple(self, filepaths, encoding=None, delimiter=None, ignore_errors=False):
        """Load multiple CSV files."""
        return load_multiple_csv(filepaths, encoding=encoding, delimiter=delimiter, ignore_errors=ignore_errors)

    def load_preview(self, filepath, preview_rows=5, **kwargs):
        """Load a CSV file and display a preview."""
        return load_csv_with_preview(filepath, preview_rows=preview_rows, **kwargs)

    def clean(
        self,
        df,
        remove_dupes=True,
        handle_missing="drop",
        clean_names=True,
        fill_value=None,
    ):
        """Apply a full cleaning pipeline to a DataFrame."""
        return clean_csv(
            df=df,
            remove_dupes=remove_dupes,
            handle_missing=handle_missing,
            clean_names=clean_names,
            fill_value=fill_value,
        )

    def remove_duplicates(self, df, subset=None, keep="first"):
        """Remove duplicate rows from a DataFrame."""
        return remove_duplicates(df, subset=subset, keep=keep)

    def handle_missing(self, df, strategy="drop", fill_value=None, columns=None, threshold=None):
        """Handle missing values in a DataFrame."""
        return handle_missing_values(df, strategy=strategy, fill_value=fill_value, columns=columns, threshold=threshold)

    def clean_column_names(self, df, strategy="lowercase"):
        """Clean and standardize column names."""
        return clean_column_names(df, strategy=strategy)

    def remove_outliers(self, df, columns, lower_bound=1.5, upper_bound=1.5):
        """Remove outliers using the IQR method."""
        return remove_outliers_iqr(df, columns, lower_bound=lower_bound, upper_bound=upper_bound)

    def describe(self, df, columns=None, include="all"):
        """Generate descriptive statistics for a DataFrame."""
        return describe_data(df, columns=columns, include=include)

    def column_summary(self, df, column):
        """Get a detailed summary of a single column."""
        return get_column_summary(df, column)

    def groupby(self, df, groupby, agg_dict):
        """Group data and apply aggregation functions."""
        return group_and_aggregate(df, groupby, agg_dict)

    def crosstab(self, df, col1, col2, values=None, aggfunc=None, margins=False):
        """Create a cross-tabulation of two columns."""
        return cross_tabulate(df, col1, col2, values=values, aggfunc=aggfunc, margins=margins)

    def filter(self, df, conditions):
        """Filter DataFrame based on column conditions."""
        return filter_data(df, conditions)

    def export(self, df, output_path, index=False, **kwargs):
        """Export DataFrame to a CSV file."""
        return export_data(df, output_path, index=index, **kwargs)


__all__ = [
    "CSVAnalyzer",
    "load_csv",
    "load_multiple_csv",
    "load_csv_with_preview",
    "remove_duplicates",
    "handle_missing_values",
    "clean_column_names",
    "remove_outliers_iqr",
    "clean_csv",
    "describe_data",
    "get_column_summary",
    "group_and_aggregate",
    "cross_tabulate",
    "filter_data",
    "export_data",
]