"""Core array and matrix routines.

All public functions accept array-like inputs and return ``numpy.ndarray``
values unless documented otherwise. Floating-point work uses ``float64`` by
default so results stay reproducible across platforms.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def as_matrix(value: ArrayLike) -> FloatArray:
    """Return ``value`` as a 2-D ``float64`` array, validating its shape."""
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError(f"expected a 2-D matrix, got {array.ndim} dimension(s)")
    return array


def matmul(a: ArrayLike, b: ArrayLike) -> FloatArray:
    """Multiply two matrices, using the fastest BLAS path available."""
    left = as_matrix(a)
    right = as_matrix(b)
    if left.shape[1] != right.shape[0]:
        raise ValueError(f"shape mismatch: {left.shape} @ {right.shape}")
    return left @ right


def gram_matrix(a: ArrayLike) -> FloatArray:
    """Return the Gram matrix ``A.T @ A``.

    For an ``m x n`` input this costs ``O(m * n**2)`` and yields an
    ``n x n`` symmetric positive-semidefinite matrix.
    """
    matrix = as_matrix(a)
    return matrix.T @ matrix


def solve(a: ArrayLike, b: ArrayLike) -> FloatArray:
    """Solve the linear system ``A x = b`` for a square ``A``."""
    matrix = as_matrix(a)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"expected a square matrix, got {matrix.shape}")
    return np.linalg.solve(matrix, np.asarray(b, dtype=np.float64))


def power_iteration(
    a: ArrayLike,
    iterations: int = 1000,
    tolerance: float = 1e-10,
    seed: int = 0,
) -> tuple[float, FloatArray]:
    """Estimate the dominant eigenvalue/vector of ``A``.

    Uses the power method, which converges when ``A`` has a unique
    eigenvalue of largest magnitude. Returns ``(eigenvalue, eigenvector)``.
    """
    matrix = as_matrix(a)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"expected a square matrix, got {matrix.shape}")
    if iterations < 1:
        raise ValueError("iterations must be >= 1")

    rng = np.random.default_rng(seed)
    vector = rng.standard_normal(matrix.shape[0])

    eigenvalue = 0.0
    for _ in range(iterations):
        product = matrix @ vector
        norm = np.linalg.norm(product)
        if norm == 0.0:
            return 0.0, vector
        vector = product / norm
        eigenvalue = float(vector @ (matrix @ vector))
        if np.linalg.norm(matrix @ vector - eigenvalue * vector) <= tolerance:
            break
    return eigenvalue, vector
