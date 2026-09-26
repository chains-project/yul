from __future__ import annotations

from pathlib import Path

import pandas as pd


class CSVDataset:
    """Loads a CSV file and provides cleaning and analysis helpers."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.df: pd.DataFrame = pd.read_csv(self.path)

    def clean(
        self,
        drop_duplicates: bool = True,
        dropna_how: str | None = "all",
        strip_strings: bool = True,
    ) -> "CSVDataset":
        """Removes duplicate rows, empty rows, and stray whitespace in-place."""
        if strip_strings:
            for col in self.df.select_dtypes(include="object").columns:
                self.df[col] = self.df[col].str.strip()

        if dropna_how is not None:
            self.df = self.df.dropna(how=dropna_how)

        if drop_duplicates:
            self.df = self.df.drop_duplicates()

        self.df = self.df.reset_index(drop=True)
        return self

    def summary(self) -> pd.DataFrame:
        """Returns descriptive statistics for numeric columns."""
        return self.df.describe()

    def column_stats(self, column: str) -> dict:
        series = self.df[column]
        stats = {
            "count": int(series.count()),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique()),
        }
        if pd.api.types.is_numeric_dtype(series):
            stats.update(
                {
                    "mean": series.mean(),
                    "median": series.median(),
                    "std": series.std(),
                    "min": series.min(),
                    "max": series.max(),
                }
            )
        return stats

    def group_by(self, by: str, agg_column: str, agg: str = "mean") -> pd.Series:
        return self.df.groupby(by)[agg_column].agg(agg)

    def to_csv(self, path: str | Path) -> None:
        self.df.to_csv(path, index=False)
