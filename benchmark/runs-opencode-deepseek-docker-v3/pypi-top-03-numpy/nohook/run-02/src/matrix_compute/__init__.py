"""Heavy numerical array and matrix computations."""

from __future__ import annotations

from .core import (
    condition_number,
    eigenvalues,
    matmul,
    random_matrix,
    singular_values,
    solve_linear,
)

__all__ = [
    "condition_number",
    "eigenvalues",
    "matmul",
    "random_matrix",
    "singular_values",
    "solve_linear",
]
