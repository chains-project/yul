"""Analysis operations for :class:`tabular.DataTable`."""

from __future__ import annotations

import math
from statistics import mean as _mean
from statistics import median as _median
from statistics import stdev as _stdev
from statistics import variance as _variance
from typing import Iterable, Optional

from ._util import is_missing, to_number
from .errors import TabularError


class AnalysisMixin:
    """Mixin providing descriptive-statistics methods to DataTable."""

    def _numbers_optional(self, column: str) -> list:
        """Return numeric values from ``column`` as floats (missing/non-numeric skipped)."""
        numbers = []
        for value in self.column(column):
            number = to_number(value)
            if number is not None:
                numbers.append(number)
        return numbers

    def _numbers(self, column: str) -> list:
        numbers = self._numbers_optional(column)
        if not numbers:
            raise TabularError(f"column {column!r} contains no numeric values")
        return numbers

    def count(self, column: Optional[str] = None) -> int:
        """Number of rows, or number of non-missing values in ``column``."""
        if column is None:
            return len(self)
        self._require(column)
        return sum(1 for value in self.column(column) if not is_missing(value))

    def sum(self, column: str) -> float:
        """Sum of the numeric values in ``column``."""
        return sum(self._numbers(column))

    def mean(self, column: str) -> float:
        """Arithmetic mean of the numeric values in ``column``."""
        return _mean(self._numbers(column))

    def median(self, column: str) -> float:
        """Median of the numeric values in ``column``."""
        return _median(self._numbers(column))

    def min(self, column: str) -> float:
        """Smallest numeric value in ``column``."""
        return min(self._numbers(column))

    def max(self, column: str) -> float:
        """Largest numeric value in ``column``."""
        return max(self._numbers(column))

    def variance(self, column: str) -> float:
        """Sample variance of the numeric values in ``column``."""
        numbers = self._numbers(column)
        if len(numbers) < 2:
            raise TabularError(f"column {column!r} needs at least two values")
        return _variance(numbers)

    def stdev(self, column: str) -> float:
        """Sample standard deviation of the numeric values in ``column``."""
        numbers = self._numbers(column)
        if len(numbers) < 2:
            raise TabularError(f"column {column!r} needs at least two values")
        return _stdev(numbers)

    def value_counts(self, column: str, dropna: bool = True) -> dict:
        """Count occurrences of each value in ``column``, most frequent first."""
        self._require(column)
        counts = {}
        for value in self.column(column):
            if is_missing(value) and dropna:
                continue
            key = value
            try:
                counts[key] = counts.get(key, 0) + 1
            except TypeError:
                text = str(key)
                counts[text] = counts.get(text, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    def describe(self, columns: Optional[Iterable[str]] = None) -> dict:
        """Return summary statistics for each column.

        Numeric columns report count/mean/min/max/median (plus stdev when at
        least two values exist); other columns report count/unique/top/freq.
        """
        target = self._resolve_columns(columns)
        summary = {}
        for column in target:
            values = self.column(column)
            present = sum(1 for value in values if not is_missing(value))
            numbers = self._numbers_optional(column)
            if numbers:
                stats = {
                    "count": present,
                    "numeric_count": len(numbers),
                    "mean": _mean(numbers),
                    "min": min(numbers),
                    "max": max(numbers),
                    "median": _median(numbers),
                }
                if len(numbers) >= 2:
                    stats["stdev"] = _stdev(numbers)
                summary[column] = stats
            else:
                counts = self.value_counts(column)
                top, freq = next(iter(counts.items()), (None, 0))
                summary[column] = {
                    "count": present,
                    "unique": len(counts),
                    "top": top,
                    "freq": freq,
                }
        return summary

    def correlation(self, x: str, y: str) -> float:
        """Pearson correlation between numeric columns ``x`` and ``y``."""
        self._require(x)
        self._require(y)
        xs, ys = [], []
        for row in self._rows:
            first = to_number(row[x])
            second = to_number(row[y])
            if first is None or second is None:
                continue
            xs.append(first)
            ys.append(second)
        if len(xs) < 2:
            raise TabularError("correlation needs at least two paired numeric values")
        mean_x = _mean(xs)
        mean_y = _mean(ys)
        covariance = sum((a - mean_x) * (b - mean_y) for a, b in zip(xs, ys))
        spread_x = math.sqrt(sum((a - mean_x) ** 2 for a in xs))
        spread_y = math.sqrt(sum((b - mean_y) ** 2 for b in ys))
        if spread_x == 0 or spread_y == 0:
            raise TabularError("correlation is undefined for constant data")
        return covariance / (spread_x * spread_y)
