"""Shared internal helpers for :mod:`csvlib`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Optional


def uniquify(names: Iterable[str]) -> list[str]:
    """Return *names* with duplicates suffixed ``_2``, ``_3``, ... to be unique."""
    seen: dict[str, int] = {}
    result: list[str] = []
    for name in names:
        if name not in seen:
            seen[name] = 1
            result.append(name)
            continue
        seen[name] += 1
        candidate = f"{name}_{seen[name]}"
        while candidate in seen:
            seen[name] += 1
            candidate = f"{name}_{seen[name]}"
        seen[candidate] = 1
        result.append(candidate)
    return result


def resolve_columns(table, columns: Optional[Any]) -> list[str]:
    """Normalize a column selector to a list of existing column names."""
    if columns is None:
        return table.columns
    if isinstance(columns, str):
        selected = [columns]
    else:
        selected = list(columns)
    unknown = [c for c in selected if c not in table.columns]
    if unknown:
        raise KeyError(f"Unknown column(s): {', '.join(map(repr, unknown))}")
    return selected


def is_missing(value: Any) -> bool:
    """Return ``True`` for values csvlib treats as missing."""
    return value is None or (isinstance(value, str) and value.strip() == "")
