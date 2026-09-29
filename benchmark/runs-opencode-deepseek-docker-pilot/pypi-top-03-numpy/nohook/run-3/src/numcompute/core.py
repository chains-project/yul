"""Array and matrix kernels implemented with NumPy."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def matrix_multiply(a: FloatArray, b: FloatArray) -> FloatArray:
    """Return the matrix product of two 2-D arrays."""
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("matrix_multiply expects 2-D arrays")
    if a.shape[1] != b.shape[0]:
        raise ValueError(f"shape mismatch: {a.shape} @ {b.shape}")
    return np.asarray(a @ b, dtype=np.float64)


def covariance(x: FloatArray) -> FloatArray:
    """Return the covariance matrix of a 2-D sample array (rows are observations)."""
    if x.ndim != 2:
        raise ValueError("covariance expects a 2-D array")
    centered = x - x.mean(axis=0, keepdims=True)
    n = x.shape[0] - 1
    if n < 1:
        raise ValueError("at least two observations are required")
    return np.asarray((centered.T @ centered) / n, dtype=np.float64)


def power_iteration(
    a: FloatArray,
    *,
    num_iter: int = 1000,
    tol: float = 1e-10,
    seed: int = 0,
) -> tuple[float, FloatArray]:
    """Estimate the dominant eigenvalue/vector of a square matrix via power iteration."""
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("power_iteration expects a square 2-D array")
    rng = np.random.default_rng(seed)
    n = a.shape[0]
    v = rng.standard_normal(n)
    v /= np.linalg.norm(v)
    eigenvalue = 0.0
    for _ in range(num_iter):
        w = a @ v
        eigenvalue_new = float(v @ w)
        norm = np.linalg.norm(w)
        if norm == 0.0:
            break
        v = w / norm
        if abs(eigenvalue_new - eigenvalue) <= tol:
            eigenvalue = eigenvalue_new
            break
        eigenvalue = eigenvalue_new
    return eigenvalue, v


def first_eigenpair(a: FloatArray) -> tuple[float, FloatArray]:
    """Return the largest-magnitude eigenvalue and its eigenvector using LAPACK."""
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("first_eigenpair expects a square 2-D array")
    values, vectors = np.linalg.eigh(a)
    index = int(np.argmax(np.abs(values)))
    return float(values[index]), np.asarray(vectors[:, index], dtype=np.float64)


def monte_carlo_pi(num_samples: int, *, seed: int | None = None) -> float:
    """Estimate pi by sampling points in the unit square."""
    if num_samples <= 0:
        raise ValueError("num_samples must be positive")
    rng = np.random.default_rng(seed)
    points = rng.random((num_samples, 2))
    inside = np.sum(np.einsum("ij,ij->i", points, points) <= 1.0)
    return float(4.0 * inside / num_samples)
