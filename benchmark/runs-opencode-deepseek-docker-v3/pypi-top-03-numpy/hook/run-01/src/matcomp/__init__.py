"""Heavy numerical array and matrix computations built on NumPy."""

from matcomp.core import (
    gram_matrix,
    matmul,
    power_iteration,
    solve,
)

__all__ = ["gram_matrix", "matmul", "power_iteration", "solve"]
__version__ = "0.1.0"
