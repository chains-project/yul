"""numlab: heavy numerical array and matrix computations."""

from numlab.linalg import (
    cholesky,
    eigenvalues,
    matrix_multiply,
    power_iteration,
    random_spd_matrix,
    singular_values,
    solve_linear_system,
)

__all__ = [
    "cholesky",
    "eigenvalues",
    "matrix_multiply",
    "power_iteration",
    "random_spd_matrix",
    "singular_values",
    "solve_linear_system",
]

__version__ = "0.1.0"
