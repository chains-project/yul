"""Core matrix routines. Keep work vectorized; avoid Python-level loops over elements."""

import numpy as np
import scipy.linalg as sla
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def solve_system(a: FloatArray, b: FloatArray) -> FloatArray:
    """Solve ``a @ x = b``, via Cholesky when ``a`` is symmetric positive definite."""
    if np.allclose(a, a.T):
        try:
            return sla.cho_solve(sla.cho_factor(a), b)
        except sla.LinAlgError:
            pass
    return sla.solve(a, b)


def spectral_summary(a: FloatArray) -> dict[str, float]:
    """Return the extreme singular values and condition number of ``a``."""
    s = sla.svdvals(a)
    return {"sigma_max": float(s[0]), "sigma_min": float(s[-1]), "cond": float(s[0] / s[-1])}
