"""High-performance numerical array and matrix routines."""

from .linear import (
    batched_matmul,
    condition_number,
    eigenvalues,
    matmul,
    solve_linear_system,
)

__all__ = [
    "matmul",
    "batched_matmul",
    "solve_linear_system",
    "eigenvalues",
    "condition_number",
]

__version__ = "0.1.0"
