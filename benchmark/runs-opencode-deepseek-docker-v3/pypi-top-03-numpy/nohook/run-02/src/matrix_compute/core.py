"""Core dense matrix routines used by the computation scripts."""

from __future__ import annotations

import numpy as np
import scipy.linalg as sla
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def random_matrix(rows: int, cols: int, *, seed: int | None = None) -> FloatArray:
    """Return a ``rows`` x ``cols`` matrix of standard normal values."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((rows, cols))


def matmul(a: FloatArray, b: FloatArray) -> FloatArray:
    """Matrix multiply ``a`` and ``b`` (BLAS-backed)."""
    return a @ b


def solve_linear(a: FloatArray, b: FloatArray) -> FloatArray:
    """Solve ``a @ x = b``.

    Uses LU decomposition for square systems and falls back to a
    least-squares solve for rectangular (over/under-determined) systems.
    """
    if a.shape[0] == a.shape[1]:
        lu, piv = sla.lu_factor(a)
        return sla.lu_solve((lu, piv), b)
    return sla.lstsq(a, b)[0]


def eigenvalues(a: FloatArray) -> NDArray[np.complex128]:
    """Return the eigenvalues of a square matrix."""
    return sla.eigvals(a)


def singular_values(a: FloatArray) -> FloatArray:
    """Return the singular values of ``a`` in descending order."""
    return sla.svd(a, compute_uv=False)


def condition_number(a: FloatArray) -> float:
    """Return the 2-norm condition number of ``a``."""
    return float(np.linalg.cond(a))
