"""Core matrix routines. Keep everything vectorized: avoid Python-level loops over elements."""

import numpy as np
import scipy.linalg as sla
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def solve_system(a: FloatArray, b: FloatArray) -> FloatArray:
    """Solve ``a @ x = b`` via LU factorization (no explicit inverse)."""
    return sla.solve(a, b, check_finite=False)


def spectral_summary(a: FloatArray) -> dict[str, float]:
    """Return basic spectral properties of a matrix."""
    s = sla.svdvals(a, check_finite=False)
    return {
        "norm_2": float(s[0]),
        "cond": float(s[0] / s[-1]) if s[-1] > 0 else float("inf"),
        "rank": float(np.sum(s > s[0] * max(a.shape) * np.finfo(a.dtype).eps)),
    }
