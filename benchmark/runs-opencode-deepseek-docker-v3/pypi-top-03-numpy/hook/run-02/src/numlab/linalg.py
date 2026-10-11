"""Core numerical routines for dense array and matrix computations."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from scipy import linalg

Array = npt.NDArray[np.float64]


def matrix_multiply(a: Array, b: Array) -> Array:
    """Multiply two matrices using the underlying BLAS implementation."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return a @ b


def solve_linear_system(a: Array, b: Array) -> Array:
    """Solve the linear system ``a @ x = b`` for ``x``."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return linalg.solve(a, b, assume_a="gen")


def eigenvalues(a: Array) -> Array:
    """Return the eigenvalues of a square matrix."""
    a = np.asarray(a, dtype=np.float64)
    return np.linalg.eigvals(a)


def singular_values(a: Array) -> Array:
    """Return the singular values of a matrix."""
    a = np.asarray(a, dtype=np.float64)
    return linalg.svdvals(a)


def cholesky(a: Array) -> Array:
    """Return the lower Cholesky factor of a symmetric positive-definite matrix."""
    a = np.asarray(a, dtype=np.float64)
    return linalg.cholesky(a, lower=True)


def power_iteration(a: Array, *, tol: float = 1e-10, max_iter: int = 1000) -> tuple[float, Array]:
    """Estimate the dominant eigenvalue and eigenvector of a square matrix."""
    a = np.asarray(a, dtype=np.float64)
    n = a.shape[0]
    vector = np.ones(n, dtype=np.float64)
    eigenvalue = 0.0
    for _ in range(max_iter):
        previous = eigenvalue
        vector = a @ vector
        norm = np.linalg.norm(vector)
        if norm == 0.0:
            return 0.0, vector
        vector /= norm
        eigenvalue = float(vector @ (a @ vector))
        if abs(eigenvalue - previous) < tol:
            break
    return eigenvalue, vector


def random_spd_matrix(n: int, *, seed: int | None = None) -> Array:
    """Generate an ``n x n`` symmetric positive-definite matrix."""
    rng = np.random.default_rng(seed)
    m = rng.standard_normal((n, n))
    return m @ m.T + n * np.eye(n)
