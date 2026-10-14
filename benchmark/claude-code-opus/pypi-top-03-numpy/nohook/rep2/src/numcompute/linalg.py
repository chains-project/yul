"""Core matrix routines built on NumPy/SciPy."""

import numpy as np
import scipy.linalg as sla
from numpy.typing import NDArray

Array = NDArray[np.float64]


def random_spd(n: int, rng: np.random.Generator) -> Array:
    """Return a random n x n symmetric positive-definite matrix."""
    a = rng.standard_normal((n, n))
    return a @ a.T + n * np.eye(n)


def solve_spd(a: Array, b: Array) -> Array:
    """Solve a @ x = b for symmetric positive-definite `a` via Cholesky."""
    c, lower = sla.cho_factor(a, check_finite=False)
    return sla.cho_solve((c, lower), b, check_finite=False)


def relative_residual(a: Array, x: Array, b: Array) -> float:
    """Return ||a @ x - b|| / ||b||."""
    return float(np.linalg.norm(a @ x - b) / np.linalg.norm(b))
