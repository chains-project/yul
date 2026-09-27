"""Cleaning operations for :class:`tabular.DataTable`.

Every method returns a new :class:`~tabular.table.DataTable`; the receiver is
never modified.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional, Sequence

from ._util import is_missing


def _coerce_value(value: Any) -> Any:
    """Convert a string to ``int`` or ``float`` when it represents a number."""
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return value
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return value


class CleaningMixin:
    """Mixin providing cleaning methods to :class:`tabular.DataTable`."""

    def _resolve_columns(self, columns: Optional[Iterable[str]]) -> list:
        if columns is None:
            return list(self._columns)
        resolved = list(columns)
        self._require_all(resolved)
        return resolved

    def select_columns(self, columns: Sequence[str]):
        """Return a table containing only ``columns``, in the given order."""
        selected = list(columns)
        self._require_all(selected)
        return self._clone(columns=selected, rows=self._rows)

    def drop_columns(self, columns: Sequence[str]):
        """Return a table with ``columns`` removed."""
        dropped = set(columns)
        self._require_all(dropped)
        remaining = [column for column in self._columns if column not in dropped]
        if not remaining:
            raise ValueError("cannot drop every column")
        return self._clone(columns=remaining, rows=self._rows)

    def rename_columns(self, mapping: Mapping[str, str]):
        """Return a table with columns renamed according to ``mapping``."""
        renamed = [mapping.get(column, column) for column in self._columns]
        if len(set(renamed)) != len(renamed):
            raise ValueError("rename would create duplicate column names")
        rows = [
            {mapping.get(column, column): row[column] for column in self._columns}
            for row in self._rows
        ]
        return self._clone(columns=renamed, rows=rows)

    def strip_whitespace(self, columns: Optional[Sequence[str]] = None):
        """Strip leading/trailing whitespace from string cells."""
        target = self._resolve_columns(columns)
        rows = []
        for row in self._rows:
            updated = dict(row)
            for column in target:
                value = updated[column]
                if isinstance(value, str):
                    updated[column] = value.strip()
            rows.append(updated)
        return self._clone(rows=rows)

    def drop_duplicates(self, subset: Optional[Sequence[str]] = None):
        """Return a table with duplicate rows removed (first occurrence kept)."""
        target = self._resolve_columns(subset)
        seen = set()
        rows = []
        for row in self._rows:
            key = tuple(row[column] for column in target)
            if key in seen:
                continue
            seen.add(key)
            rows.append(dict(row))
        return self._clone(rows=rows)

    def drop_missing(self, subset: Optional[Sequence[str]] = None, how: str = "any"):
        """Drop rows with missing values.

        ``how="any"`` removes a row when any selected cell is missing;
        ``how="all"`` removes it only when every selected cell is missing.
        """
        if how not in ("any", "all"):
            raise ValueError("how must be 'any' or 'all'")
        target = self._resolve_columns(subset)
        rows = []
        for row in self._rows:
            missing = sum(1 for column in target if is_missing(row[column]))
            if how == "any" and missing:
                continue
            if how == "all" and missing == len(target):
                continue
            rows.append(dict(row))
        return self._clone(rows=rows)

    def fill_missing(self, value: Any, subset: Optional[Sequence[str]] = None):
        """Replace missing cells with ``value``.

        ``value`` may be a scalar applied to every column or a mapping of
        column name to replacement.
        """
        target = self._resolve_columns(subset)
        rows = []
        for row in self._rows:
            updated = dict(row)
            for column in target:
                if not is_missing(updated[column]):
                    continue
                if isinstance(value, Mapping):
                    replacement = value.get(column)
                    if replacement is not None:
                        updated[column] = replacement
                else:
                    updated[column] = value
            rows.append(updated)
        return self._clone(rows=rows)

    def convert_types(self, columns: Optional[Sequence[str]] = None):
        """Convert numeric-looking string columns to ``int`` or ``float``.

        A column is converted only when every non-missing value parses as a
        number; otherwise it is left untouched.
        """
        target = self._resolve_columns(columns)
        convertible = set()
        for column in target:
            values = [row[column] for row in self._rows if not is_missing(row[column])]
            if values and all(
                isinstance(_coerce_value(value), (int, float))
                and not isinstance(value, bool)
                for value in values
            ):
                convertible.add(column)

        rows = []
        for row in self._rows:
            updated = dict(row)
            for column in convertible:
                if not is_missing(updated[column]):
                    updated[column] = _coerce_value(updated[column])
            rows.append(updated)
        return self._clone(rows=rows)
