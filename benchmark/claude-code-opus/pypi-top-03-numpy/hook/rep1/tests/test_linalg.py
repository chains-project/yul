import numpy as np

from numcompute.linalg import random_spd, solve_spd


def test_solve_spd_matches_numpy():
    rng = np.random.default_rng(42)
    a = random_spd(50, rng)
    b = rng.standard_normal(50)
    np.testing.assert_allclose(solve_spd(a, b), np.linalg.solve(a, b), rtol=1e-10)


def test_random_spd_is_symmetric_positive_definite():
    a = random_spd(20, np.random.default_rng(0))
    np.testing.assert_allclose(a, a.T)
    assert np.all(np.linalg.eigvalsh(a) > 0)
