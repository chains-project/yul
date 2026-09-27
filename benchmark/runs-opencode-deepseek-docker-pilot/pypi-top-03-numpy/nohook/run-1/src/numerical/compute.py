from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def _as_float_array(a: ArrayLike) -> FloatArray:
    return np.asarray(a, dtype=np.float64)


def matmul(a: ArrayLike, b: ArrayLike) -> FloatArray:
    """Matrix multiply two arrays."""
    return _as_float_array(a) @ _as_float_array(b)


def matrix_power(a: ArrayLike, n: int) -> FloatArray:
    """Raise a square matrix to the integer power ``n``."""
    return np.linalg.matrix_power(_as_float_array(a), n)


def solve_linear_system(a: ArrayLike, b: ArrayLike) -> FloatArray:
    """Solve the linear system ``A x = b``."""
    return np.linalg.solve(_as_float_array(a), _as_float_array(b))


def svd(a: ArrayLike) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Return the singular value decomposition of ``a``."""
    return np.linalg.svd(_as_float_array(a), full_matrices=False)


def eigen(a: ArrayLike) -> tuple[FloatArray, FloatArray]:
    """Return eigenvalues and eigenvectors of a square matrix."""
    return np.linalg.eig(_as_float_array(a))
