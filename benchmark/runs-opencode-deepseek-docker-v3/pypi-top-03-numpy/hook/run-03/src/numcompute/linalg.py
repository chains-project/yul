"""Core numerical linear-algebra routines built on NumPy and SciPy."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import scipy.linalg

Array = npt.NDArray[np.float64]
Eigenvalues = npt.NDArray[np.float64] | npt.NDArray[np.complex128]


def as_matrix(a: npt.ArrayLike, *, square: bool = False) -> Array:
    """Return ``a`` as a 2-D float64 array, validating its shape."""
    matrix = np.asarray(a, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError(f"expected a 2-D array, got {matrix.ndim} dimensions")
    if square and matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"expected a square matrix, got shape {matrix.shape}")
    return matrix


def matmul(a: npt.ArrayLike, b: npt.ArrayLike) -> Array:
    """Multiply two matrices using NumPy's BLAS-backed matmul operator."""
    left = as_matrix(a)
    right = as_matrix(b)
    if left.shape[1] != right.shape[0]:
        raise ValueError(
            f"cannot multiply {left.shape} by {right.shape}: "
            "inner dimensions do not match"
        )
    return left @ right


def solve(a: npt.ArrayLike, b: npt.ArrayLike) -> Array:
    """Solve the linear system ``A x = b`` using LU decomposition."""
    matrix = as_matrix(a, square=True)
    rhs = np.asarray(b, dtype=np.float64)
    return np.asarray(scipy.linalg.solve(matrix, rhs, assume_a="gen"))


def eigenvalues(a: npt.ArrayLike) -> Eigenvalues:
    """Return the eigenvalues of a square matrix."""
    return np.linalg.eigvals(as_matrix(a, square=True))


def singular_values(a: npt.ArrayLike) -> Array:
    """Return the singular values of a matrix in descending order."""
    return np.linalg.svd(as_matrix(a), compute_uv=False)


def condition_number(a: npt.ArrayLike) -> float:
    """Return the 2-norm condition number of a square matrix."""
    matrix = as_matrix(a, square=True)
    return float(np.linalg.cond(matrix, p=2))


def matrix_power(a: npt.ArrayLike, n: int) -> Array:
    """Raise a square matrix to the integer power ``n``."""
    return np.linalg.matrix_power(as_matrix(a, square=True), n)


def random_spd(n: int, *, seed: int | None = None) -> Array:
    """Generate a random symmetric positive-definite ``n x n`` matrix."""
    rng = np.random.default_rng(seed)
    m = rng.standard_normal((n, n))
    return m @ m.T + n * np.eye(n)
