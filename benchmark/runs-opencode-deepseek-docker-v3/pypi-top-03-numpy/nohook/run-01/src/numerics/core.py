"""Core numerical array and matrix routines."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from scipy import linalg

Array = npt.NDArray[np.floating] | npt.NDArray[np.complexfloating]


def matmul(a: Array, b: Array) -> Array:
    """Matrix-multiply two dense arrays using BLAS-backed ``np.matmul``.

    For very large products consider ``float32`` and a chunked implementation
    to reduce peak memory, or a GPU backend such as CuPy.
    """
    return np.matmul(a, b)


def solve(a: Array, b: Array) -> Array:
    """Solve the linear system ``a @ x = b`` via an LU factorization."""
    return linalg.solve(a, b)


def eigenvalues(a: Array) -> npt.NDArray[np.floating]:
    """Return the eigenvalues of a Hermitian matrix in ascending order."""
    values = linalg.eigvalsh(a)
    return np.asarray(values, dtype=np.float64)


def conditioning(a: Array) -> float:
    """Return the 2-norm condition number of a square matrix."""
    return float(np.linalg.cond(a, p=2))
