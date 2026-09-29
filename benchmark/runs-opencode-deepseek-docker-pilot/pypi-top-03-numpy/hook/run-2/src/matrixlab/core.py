from __future__ import annotations

import numpy as np

ArrayLike = np.ndarray | list | tuple


def _as_matrix(a: ArrayLike, *, dtype: np.dtype = np.float64) -> np.ndarray:
    arr = np.asarray(a, dtype=dtype)
    if arr.ndim != 2:
        raise ValueError(f"expected a 2-D matrix, got {arr.ndim}-D array")
    return arr


def _as_vector(v: ArrayLike, *, dtype: np.dtype = np.float64) -> np.ndarray:
    arr = np.asarray(v, dtype=dtype)
    if arr.ndim != 1:
        raise ValueError(f"expected a 1-D vector, got {arr.ndim}-D array")
    return arr


def matmul_blocked(
    a: ArrayLike,
    b: ArrayLike,
    *,
    block_size: int | None = None,
) -> np.ndarray:
    a = _as_matrix(a)
    b = _as_matrix(b)
    if a.shape[1] != b.shape[0]:
        raise ValueError(f"shape mismatch: {a.shape} @ {b.shape}")

    m, k = a.shape
    n = b.shape[1]
    out = np.empty((m, n), dtype=a.dtype)

    if block_size is None:
        block_size = max(64, int(np.sqrt(k)) or 1)

    for i in range(0, m, block_size):
        i_end = min(i + block_size, m)
        for j in range(0, n, block_size):
            j_end = min(j + block_size, n)
            acc = np.zeros((i_end - i, j_end - j), dtype=a.dtype)
            for p in range(0, k, block_size):
                p_end = min(p + block_size, k)
                acc += a[i:i_end, p:p_end] @ b[p:p_end, j:j_end]
            out[i:i_end, j:j_end] = acc
    return out


def matvec(a: ArrayLike, v: ArrayLike) -> np.ndarray:
    a = _as_matrix(a)
    v = _as_vector(v)
    if a.shape[1] != v.shape[0]:
        raise ValueError(f"shape mismatch: {a.shape} @ {v.shape}")
    return a @ v


def solve_linear_system(a: ArrayLike, b: ArrayLike) -> np.ndarray:
    a = _as_matrix(a)
    b = _as_vector(b)
    if a.shape[0] != a.shape[1]:
        raise ValueError(f"expected a square matrix, got {a.shape}")
    if a.shape[0] != b.shape[0]:
        raise ValueError(f"shape mismatch: {a.shape} vs {b.shape}")
    return np.linalg.solve(a, b)


def eigen_decomposition(a: ArrayLike, *, symmetric: bool = True) -> tuple[np.ndarray, np.ndarray]:
    a = _as_matrix(a)
    if a.shape[0] != a.shape[1]:
        raise ValueError(f"expected a square matrix, got {a.shape}")
    if symmetric:
        return np.linalg.eigh(a)
    values, vectors = np.linalg.eig(a)
    order = np.argsort(values)
    return values[order], vectors[:, order]
