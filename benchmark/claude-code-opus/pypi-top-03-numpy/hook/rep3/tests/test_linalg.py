import numpy as np
from numpy.testing import assert_allclose

from numcompute import solve_system, spectral_summary


def test_solve_system_matches_known_solution():
    rng = np.random.default_rng(42)
    a = rng.standard_normal((50, 50)) + 50 * np.eye(50)
    x_true = rng.standard_normal(50)
    assert_allclose(solve_system(a, a @ x_true), x_true, rtol=1e-10)


def test_spectral_summary_identity():
    summary = spectral_summary(np.eye(10))
    assert summary["norm_2"] == 1.0
    assert summary["cond"] == 1.0
    assert summary["rank"] == 10
