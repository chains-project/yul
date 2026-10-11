"""numcompute: numerical array and matrix computation toolkit."""

from __future__ import annotations

from numcompute.linalg import (
    as_matrix,
    condition_number,
    eigenvalues,
    matmul,
    matrix_power,
    random_spd,
    singular_values,
    solve,
)

__all__ = [
    "as_matrix",
    "condition_number",
    "eigenvalues",
    "matmul",
    "matrix_power",
    "random_spd",
    "singular_values",
    "solve",
]

__version__ = "0.1.0"
