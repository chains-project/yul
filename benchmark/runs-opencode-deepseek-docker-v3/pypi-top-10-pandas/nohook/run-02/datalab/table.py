"""Core tabular structures for :mod:`datalab`.

A :class:`Table` is a lightweight, dependency-free container for tabular
data.  Column names are stored separately from the row data and individual
:class:`Column` objects expose helpers used by the cleaning and analysis
modules.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence

__all__ = ["Table", "Column", "ColumnNotFoundError", "to_number", "is_missing"]


MISSING_TOKENS = frozenset({"", "na", "n/a", "nan", "null", "none", "-"})


class ColumnNotFoundError(KeyError):
    """Raised when a requested column does not exist in a table."""

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"column not found: {self.name!r}"


def is_missing(value: Any) -> bool:
    """Return ``True`` when *value* represents a missing entry.

    Missing entries are ``None`` and the common textual placeholders used in
    CSV exports (``""``, ``"NA"``, ``"N/A"``, ``"null"``, ``"none"`` and
    ``"-"``), matched case-insensitively after stripping whitespace.
    """
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    if isinstance(value, str):
        return value.strip().lower() in MISSING_TOKENS
    return False


def to_number(value: Any) -> Optional[float]:
    """Best-effort conversion of *value* to an ``int`` or ``float``.

    Returns ``None`` when the value is missing or cannot be interpreted as a
    number.  Common representations such as ``"1,234.5"``, ``"$1,234"``,
    ``"(1,200)"`` and ``"50%"`` are understood.
    """
    if value is None or isinstance(value, bool):
        if isinstance(value, bool):
            return int(value)
        return None
    if isinstance(value, (int, float)):
        if value != value:  # NaN
            return None
        return value
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text or text.lower() in MISSING_TOKENS:
        return None

    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1].strip()

    percent = text.endswith("%")
    if percent:
        text = text[:-1].strip()

    text = text.replace(",", "").replace("_", "")
    if text.startswith("$"):
        text = text[1:]
    if text.startswith("+"):
        text = text[1:]

    try:
        number = float(text)
    except ValueError:
        return None

    if negative:
        number = -number
    if percent:
        number /= 100.0

    if number.is_integer() and not any(c in text for c in ".eE"):
        return int(number)
    return number


class Column:
    """A single named column of values."""

    __slots__ = ("_name", "_values")

    def __init__(self, name: str, values: Iterable[Any]):
        self._name = name
        self._values: List[Any] = list(values)

    @property
    def name(self) -> str:
        return self._name

    @property
    def values(self) -> List[Any]:
        return list(self._values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index):
        return self._values[index]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Column):
            return NotImplemented
        return self._name == other._name and self._values == other._values

    def __repr__(self) -> str:
        return f"Column(name={self._name!r}, values={self._values!r})"

    def to_numeric(self) -> List[Optional[float]]:
        """Return the column parsed as numbers, with ``None`` for misses."""
        return [to_number(value) for value in self._values]

    def to_python(self) -> List[Any]:
        """Return every value, replacing missing tokens with ``None``."""
        return [None if is_missing(value) else value for value in self._values]

    def dropna(self) -> "Column":
        """Return a new column without missing values."""
        return Column(self._name, (v for v in self._values if not is_missing(v)))

    def unique(self) -> List[Any]:
        """Return the distinct non-missing values in first-seen order."""
        seen: List[Any] = []
        for value in self._values:
            if is_missing(value):
                continue
            if value not in seen:
                seen.append(value)
        return seen

    def is_numeric(self) -> bool:
        """Return ``True`` when every non-missing value parses as a number."""
        found = False
        for value in self._values:
            if is_missing(value):
                continue
            if to_number(value) is None:
                return False
            found = True
        return found

    def missing_count(self) -> int:
        return sum(1 for value in self._values if is_missing(value))


class Table:
    """An immutable-by-convention table of headers and rows.

    Cleaning helpers always return *new* :class:`Table` instances rather than
    mutating in place, which makes pipelines easy to reason about.
    """

    def __init__(self, headers: Sequence[str], rows: Iterable[Sequence[Any]]):
        if isinstance(headers, (str, bytes)) or not hasattr(headers, "__iter__"):
            raise TypeError("headers must be a sequence of strings")

        header_list = [self._check_header(h) for h in headers]
        if not header_list:
            raise ValueError("a table must have at least one column")
        if len(set(header_list)) != len(header_list):
            raise ValueError(f"duplicate column names: {header_list}")

        width = len(header_list)
        row_list: List[List[Any]] = []
        for position, row in enumerate(rows):
            if isinstance(row, (str, bytes)) or not hasattr(row, "__iter__"):
                raise TypeError(f"row {position} is not a sequence")
            values = list(row)
            if len(values) != width:
                raise ValueError(
                    f"row {position} has {len(values)} values, expected {width}"
                )
            row_list.append(values)

        self._headers = header_list
        self._rows = row_list

    @staticmethod
    def _check_header(header: Any) -> str:
        if header is None:
            raise ValueError("column names cannot be None")
        name = str(header).strip()
        if not name:
            raise ValueError("column names cannot be empty")
        return name

    @classmethod
    def from_dicts(
        cls, records: Iterable[Mapping[str, Any]], headers: Optional[Sequence[str]] = None
    ) -> "Table":
        """Build a table from an iterable of mappings."""
        records = list(records)
        if headers is None:
            headers = []
            for record in records:
                for key in record:
                    if key not in headers:
                        headers.append(key)
        row_list = [[record.get(header) for header in headers] for record in records]
        return cls(headers, row_list)

    @property
    def headers(self) -> List[str]:
        return list(self._headers)

    @property
    def rows(self) -> List[List[Any]]:
        return [list(row) for row in self._rows]

    @property
    def width(self) -> int:
        return len(self._headers)

    @property
    def height(self) -> int:
        return len(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        headers = self._headers
        for row in self._rows:
            yield dict(zip(headers, row))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Table):
            return NotImplemented
        return self._headers == other._headers and self._rows == other._rows

    def __repr__(self) -> str:
        preview = self._rows[:5]
        return f"Table(headers={self._headers!r}, rows={preview!r}, height={len(self)})"

    def __getitem__(self, name: str) -> Column:
        if not isinstance(name, str):
            raise TypeError("column access expects a string name")
        return self.column(name)

    def column(self, name: str) -> Column:
        """Return the named column as a :class:`Column`."""
        try:
            index = self._headers.index(name)
        except ValueError:
            raise ColumnNotFoundError(name) from None
        return Column(name, (row[index] for row in self._rows))

    def has_column(self, name: str) -> bool:
        return name in self._headers

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Return the rows as a list of dictionaries."""
        return list(self)

    def to_rows(self) -> List[List[Any]]:
        return self.rows

    def head(self, n: int = 5) -> "Table":
        return Table(self._headers, self._rows[:n])

    def tail(self, n: int = 5) -> "Table":
        return Table(self._headers, self._rows[-n:] if n > 0 else [])

    def select(self, *columns: str) -> "Table":
        """Return a table containing only *columns*, in the given order."""
        indices = []
        for name in columns:
            try:
                indices.append(self._headers.index(name))
            except ValueError:
                raise ColumnNotFoundError(name) from None
        return Table(list(columns), ([row[i] for i in indices] for row in self._rows))

    def copy(self) -> "Table":
        return Table(self._headers, self._rows)

    def with_column(self, name: str, values: Iterable[Any]) -> "Table":
        """Return a copy with a new column appended."""
        if name in self._headers:
            raise ValueError(f"column already exists: {name!r}")
        values = list(values)
        if len(values) != len(self._rows):
            raise ValueError(
                f"column {name!r} has {len(values)} values, expected {len(self._rows)}"
            )
        headers = self._headers + [self._check_header(name)]
        rows = [row + [value] for row, value in zip(self._rows, values)]
        return Table(headers, rows)
