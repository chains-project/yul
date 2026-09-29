"""Core linear-algebra kernels for array and matrix computations.

All routines operate on ``numpy.ndarray`` objects and delegate the heavy
lifting to the BLAS/LAPACK-backed NumPy and SciPy implementations so that
workloads stay in compiled code rather than Python loops.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import linalg

Matrix = NDArray[np.floating]


def _as_matrix(a: ArrayLike, name: str) -> Matrix:
    arr = np.asarray(a, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be 2-D, got {arr.ndim}-D")
    return arr


def matmul(a: ArrayLike, b: ArrayLike) -> Matrix:
    """Multiply two matrices, validating inner dimensions first."""
    left = _as_matrix(a, "a")
    right = _as_matrix(b, "b")
    if left.shape[1] != right.shape[0]:
        raise ValueError(
            f"shapes {left.shape} and {right.shape} are not aligned"
        )
    return left @ right


def batched_matmul(a: ArrayLike, b: ArrayLike) -> NDArray[np.floating]:
    """Multiply stacks of matrices with shapes ``(..., m, k)`` and ``(..., k, n)``."""
    left = np.asarray(a, dtype=np.float64)
    right = np.asarray(b, dtype=np.float64)
    if left.ndim < 2 or right.ndim < 2:
        raise ValueError("batched operands must have at least 2 dimensions")
    if left.shape[-1] != right.shape[-2]:
        raise ValueError(
            f"inner dimensions {left.shape[-1]} and {right.shape[-2]} do not match"
        )
    return np.matmul(left, right)


def solve_linear_system(a: ArrayLike, b: ArrayLike) -> NDArray[np.floating]:
    """Solve ``A x = b`` using a partial-pivot LU factorization."""
    coeffs = _as_matrix(a, "a")
    if coeffs.shape[0] != coeffs.shape[1]:
        raise ValueError(f"a must be square, got {coeffs.shape}")
    rhs = np.asarray(b, dtype=np.float64)
    if rhs.shape[0] != coeffs.shape[0]:
        raise ValueError(
            f"b has {rhs.shape[0]} rows but a has {coeffs.shape[0]}"
        )
    return linalg.solve(coeffs, rhs, assume_a="gen")


def eigenvalues(a: ArrayLike) -> NDArray[np.complex128]:
    """Return the eigenvalues of a square matrix.

    Symmetric/Hermitian inputs take the cheaper real eigensolver path.
    """
    matrix = _as_matrix(a, "a")
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"a must be square, got {matrix.shape}")
    if np.allclose(matrix, matrix.T):
        return np.linalg.eigvalsh(matrix)
    return np.linalg.eigvals(matrix)


def condition_number(a: ArrayLike) -> float:
    """Return the 2-norm condition number of a square matrix."""
    matrix = _as_matrix(a, "a")
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"a must be square, got {matrix.shape}")
    return float(np.linalg.cond(matrix, p=2))
