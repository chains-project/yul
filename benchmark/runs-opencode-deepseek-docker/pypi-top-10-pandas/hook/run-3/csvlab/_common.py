"""Internal helpers shared across csvlab modules."""

from __future__ import annotations

from typing import Any


def is_number(value: Any) -> bool:
    """True for int/float but not bool (booleans are treated as categorical)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)
