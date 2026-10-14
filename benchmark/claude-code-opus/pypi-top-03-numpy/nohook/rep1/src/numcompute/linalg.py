"""Core matrix routines. Keep work vectorized; avoid Python-level loops over elements."""

import numpy as np
import scipy.linalg
from numpy.typing import ArrayLike, NDArray


def random_spd(n: int, rng: np.random.Generator) -> NDArray[np.float64]:
    """Return a random symmetric positive-definite n x n matrix."""
    a = rng.standard_normal((n, n))
    return a @ a.T + n * np.eye(n)


def solve_spd(a: ArrayLike, b: ArrayLike) -> NDArray[np.float64]:
    """Solve a @ x = b for symmetric positive-definite a via Cholesky."""
    c, lower = scipy.linalg.cho_factor(np.asarray(a, dtype=np.float64))
    return scipy.linalg.cho_solve((c, lower), np.asarray(b, dtype=np.float64))


def relative_residual(a: ArrayLike, x: ArrayLike, b: ArrayLike) -> float:
    """Return ||a @ x - b|| / ||b||."""
    a, x, b = np.asarray(a), np.asarray(x), np.asarray(b)
    return float(np.linalg.norm(a @ x - b) / np.linalg.norm(b))
