class CsvDataError(Exception):
    """Base class for all errors raised by :mod:`csvdata`."""


class CsvLoadError(CsvDataError):
    """Raised when a CSV source cannot be read or parsed."""


class ColumnNotFoundError(CsvDataError, KeyError):
    """Raised when a requested column is not present in a table."""

    def __str__(self):
        return f"column not found: {self.args[0]!r}"


class CleaningError(CsvDataError):
    """Raised when a cleaning operation cannot be completed."""


class AnalysisError(CsvDataError):
    """Raised when an analysis operation cannot be completed."""
