"""Core dense linear algebra routines."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import linalg

FloatArray = NDArray[np.float64]


def matmul(a: FloatArray, b: FloatArray) -> FloatArray:
    """Return the matrix product ``a @ b``."""
    return np.asarray(a) @ np.asarray(b)


def solve(a: FloatArray, b: FloatArray) -> FloatArray:
    """Solve the linear system ``a x = b`` for ``x``."""
    return np.asarray(linalg.solve(a, b), dtype=np.float64)


def eigvals(a: FloatArray) -> NDArray[np.complex128]:
    """Return the eigenvalues of a square matrix."""
    return np.asarray(linalg.eigvals(a), dtype=np.complex128)


def determinant(a: FloatArray) -> float:
    """Return the determinant of a square matrix."""
    return float(linalg.det(a))


def inverse(a: FloatArray) -> FloatArray:
    """Return the inverse of a square matrix."""
    return np.asarray(linalg.inv(a), dtype=np.float64)
