"""Internal helpers shared across the tabular package."""

from __future__ import annotations

from typing import Any, Optional


def is_missing(value: Any) -> bool:
    """Return True for values treated as missing (``None`` or blank strings)."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def to_number(value: Any) -> Optional[float]:
    """Coerce ``value`` to a float, or return ``None`` if it is not numeric."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None
