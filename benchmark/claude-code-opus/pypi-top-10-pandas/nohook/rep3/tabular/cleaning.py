"""Value parsing, type inference, and name normalization."""

from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any, Iterable

MISSING_TOKENS = frozenset({"", "na", "n/a", "nan", "null", "none", "-", "?"})

_TRUE = {"true", "yes", "y", "t"}
_FALSE = {"false", "no", "n", "f"}
_INT_RE = re.compile(r"[+-]?\d+")
# Digit strings with a leading zero ("00501") are identifiers, not numbers.
_LEADING_ZERO_RE = re.compile(r"[+-]?0\d+")
# Type preference: the first type every non-missing value parses as wins.
_TYPE_ORDER = ("int", "float", "bool", "date", "datetime", "str")


def is_missing(value: Any, missing: Iterable[str] | None = None) -> bool:
    """True for ``None``, NaN, and strings in the missing-token set."""
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    if isinstance(value, str):
        tokens = MISSING_TOKENS if missing is None else missing
        return value.strip().lower() in tokens
    return False


def _parse_as(text: str, kind: str) -> Any:
    """Parse ``text`` as ``kind``; raise ValueError if it doesn't fit."""
    s = text.strip()
    if kind in ("int", "float") and _LEADING_ZERO_RE.fullmatch(s):
        raise ValueError(text)
    if kind == "int":
        s = s.replace(",", "")
        if not _INT_RE.fullmatch(s):
            raise ValueError(text)
        return int(s)
    if kind == "float":
        s = s.replace(",", "")
        if s.endswith("%"):
            return float(s[:-1]) / 100
        result = float(s)
        if math.isnan(result):
            raise ValueError(text)
        return result
    if kind == "bool":
        low = s.lower()
        if low in _TRUE:
            return True
        if low in _FALSE:
            return False
        raise ValueError(text)
    if kind == "date":
        return date.fromisoformat(s)
    if kind == "datetime":
        return datetime.fromisoformat(s)
    return s


def parse_value(text: Any, missing: Iterable[str] | None = None) -> Any:
    """Convert a single raw value to the most specific Python type."""
    if is_missing(text, missing):
        return None
    if not isinstance(text, str):
        return text
    for kind in _TYPE_ORDER:
        try:
            return _parse_as(text, kind)
        except ValueError:
            continue
    return text.strip()


def infer_type(values: Iterable[Any], missing: Iterable[str] | None = None) -> str:
    """Return the narrowest type name that every non-missing value fits.

    One of ``"int"``, ``"float"``, ``"bool"``, ``"date"``, ``"datetime"``,
    ``"str"``. An all-missing column is ``"str"``.
    """
    present = [v for v in values if not is_missing(v, missing)]
    if not present:
        return "str"
    for kind in _TYPE_ORDER[:-1]:
        try:
            for v in present:
                _parse_as(str(v), kind)
        except ValueError:
            continue
        return kind
    return "str"


def convert_column(
    values: Iterable[Any], kind: str, missing: Iterable[str] | None = None
) -> list:
    """Convert raw values to ``kind``; missing values become ``None``.

    Values that don't fit ``kind`` also become ``None``.
    """
    out = []
    for v in values:
        if is_missing(v, missing):
            out.append(None)
            continue
        try:
            out.append(_parse_as(str(v), kind))
        except ValueError:
            out.append(None)
    return out


def normalize_name(name: str) -> str:
    """``" Total Sales ($) "`` -> ``"total_sales"``."""
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name.strip())
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return name or "column"
