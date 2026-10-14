"""Core matrix routines built on NumPy/SciPy (vectorized, BLAS/LAPACK-backed)."""

import numpy as np
import scipy.linalg as sla
from numpy.typing import NDArray


def random_spd(n: int, rng: np.random.Generator) -> NDArray[np.float64]:
    """Return a random symmetric positive-definite n x n matrix."""
    a = rng.standard_normal((n, n))
    return a @ a.T + n * np.eye(n)


def solve_spd(a: NDArray[np.float64], b: NDArray[np.float64]) -> NDArray[np.float64]:
    """Solve a @ x = b for symmetric positive-definite `a` via Cholesky."""
    c, lower = sla.cho_factor(a, check_finite=False)
    return sla.cho_solve((c, lower), b, check_finite=False)
