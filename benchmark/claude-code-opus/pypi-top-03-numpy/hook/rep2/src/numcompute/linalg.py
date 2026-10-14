"""Linear algebra routines."""

import numpy as np
import scipy.linalg
from numpy.typing import ArrayLike, NDArray


def solve_linear_system(a: ArrayLike, b: ArrayLike) -> NDArray[np.float64]:
    """Solve ``a @ x = b`` for ``x``.

    Uses an LU factorization rather than forming an explicit inverse,
    which is both faster and more numerically stable.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError(f"expected a square matrix, got shape {a.shape}")
    return scipy.linalg.solve(a, b)
