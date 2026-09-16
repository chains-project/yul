"""Core numerical operations for arrays and matrices."""

import numpy as np


def matmul(a: np.ndarray, b: np.ndarray, parallel: bool = False) -> np.ndarray:
    """Multiply two matrices with optional parallelization hints."""
    return np.dot(a, b)


def eigenvalues(a: np.ndarray, k: int | None = None) -> np.ndarray:
    """Compute eigenvalues of a square matrix.

    Args:
        a: Square input matrix.
        k: If given, return the k largest eigenvalues by magnitude.
    """
    vals = np.linalg.eigvals(a)
    if k is not None:
        idx = np.argsort(-np.abs(vals))[:k]
        vals = vals[idx]
    return np.sort(vals)[::-1]


def svd(a: np.ndarray, compute_uv: bool = True, n: int | None = None) -> np.ndarray | tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform singular value decomposition.

    Args:
        a: Input matrix.
        compute_uv: Whether to return U and V matrices.
        n: If given, return only the first n singular values/vectors.
    """
    if compute_uv:
        u, s, vt = np.linalg.svd(a, full_matrices=False)
        if n is not None:
            return u[:, :n], s[:n], vt[:n, :]
        return u, s, vt
    else:
        s = np.linalg.svd(a, compute_uv=False)
        if n is not None:
            return s[:n]
        return s


def lu_decomposition(a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform LU decomposition with partial pivoting.

    Returns:
        Permutation matrix P, lower triangular L, upper triangular U.
    """
    lu, piv = np.linalg.lu(a)
    n = a.shape[0]
    p = np.eye(n)[piv]
    l = np.tril(lu, -1) * np.eye(n) + np.triu(lu)
    u = np.triu(lu)
    return p, l, u


def condition_number(a: np.ndarray) -> float:
    """Compute the condition number of a matrix (2-norm)."""
    return np.linalg.cond(a)


def matrix_power(a: np.ndarray, n: int) -> np.ndarray:
    """Raise a square matrix to an integer power."""
    return np.linalg.matrix_power(a, n)


def solve_system(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solve a linear system Ax = b.

    Args:
        a: Coefficient matrix (n x n).
        b: Right-hand side vector or matrix (n,) or (n, k).
    """
    return np.linalg.solve(a, b)