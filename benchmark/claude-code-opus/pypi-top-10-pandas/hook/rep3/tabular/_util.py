"""Helpers shared across modules."""

from __future__ import annotations

from typing import Any, Iterable


def is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and value != value)  # NaN


def is_numeric(values: Iterable[Any]) -> bool:
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)
