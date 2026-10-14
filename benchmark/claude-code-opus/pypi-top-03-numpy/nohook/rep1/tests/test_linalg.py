import numpy as np
import pytest

from numcompute.linalg import random_spd, relative_residual, solve_spd


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(42)


def test_random_spd_is_symmetric_positive_definite(rng):
    a = random_spd(50, rng)
    np.testing.assert_allclose(a, a.T)
    assert np.all(np.linalg.eigvalsh(a) > 0)


def test_solve_spd_matches_numpy(rng):
    a = random_spd(100, rng)
    b = rng.standard_normal(100)
    x = solve_spd(a, b)
    np.testing.assert_allclose(x, np.linalg.solve(a, b), rtol=1e-10)
    assert relative_residual(a, x, b) < 1e-12
