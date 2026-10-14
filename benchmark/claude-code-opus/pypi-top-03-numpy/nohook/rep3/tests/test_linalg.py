import numpy as np
import pytest

from numcompute import solve_system, spectral_summary


@pytest.fixture
def rng():
    return np.random.default_rng(42)


def test_solve_spd(rng):
    m = rng.standard_normal((50, 50))
    a = m @ m.T + 50 * np.eye(50)
    b = rng.standard_normal(50)
    np.testing.assert_allclose(a @ solve_system(a, b), b, atol=1e-10)


def test_solve_general(rng):
    a = rng.standard_normal((50, 50)) + 10 * np.eye(50)
    b = rng.standard_normal(50)
    np.testing.assert_allclose(a @ solve_system(a, b), b, atol=1e-10)


def test_spectral_summary_identity():
    s = spectral_summary(np.eye(5))
    assert s == {"sigma_max": 1.0, "sigma_min": 1.0, "cond": 1.0}
