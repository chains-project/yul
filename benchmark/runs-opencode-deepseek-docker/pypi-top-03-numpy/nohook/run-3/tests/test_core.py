import numpy as np
import pytest

from numcompute.core import (
    covariance,
    first_eigenpair,
    matrix_multiply,
    monte_carlo_pi,
    power_iteration,
)


def test_matrix_multiply_matches_numpy() -> None:
    a = np.arange(12, dtype=np.float64).reshape(3, 4)
    b = np.arange(8, dtype=np.float64).reshape(4, 2)
    np.testing.assert_allclose(matrix_multiply(a, b), a @ b)


def test_matrix_multiply_shape_mismatch() -> None:
    with pytest.raises(ValueError):
        matrix_multiply(np.ones((2, 3)), np.ones((2, 3)))


def test_covariance_matches_numpy() -> None:
    rng = np.random.default_rng(0)
    x = rng.standard_normal((500, 4))
    np.testing.assert_allclose(covariance(x), np.cov(x, rowvar=False), rtol=1e-10)


def test_power_iteration_finds_dominant_eigenvalue() -> None:
    rng = np.random.default_rng(1)
    q, _ = np.linalg.qr(rng.standard_normal((50, 50)))
    values = np.linspace(1.0, 10.0, 50)
    a = q @ np.diag(values) @ q.T
    eigenvalue, vector = power_iteration(a, seed=3)
    assert eigenvalue == pytest.approx(10.0, rel=1e-6)
    residual = np.linalg.norm(a @ vector - eigenvalue * vector)
    assert residual < 1e-4


def test_first_eigenpair_matches_lapack() -> None:
    rng = np.random.default_rng(2)
    a = rng.standard_normal((30, 30))
    a = a + a.T
    value, vector = first_eigenpair(a)
    assert value == pytest.approx(np.linalg.eigvalsh(a).max())
    np.testing.assert_allclose(a @ vector, value * vector, atol=1e-8)


def test_monte_carlo_pi_converges() -> None:
    assert monte_carlo_pi(2_000_000, seed=7) == pytest.approx(np.pi, abs=0.01)


def test_monte_carlo_pi_rejects_bad_input() -> None:
    with pytest.raises(ValueError):
        monte_carlo_pi(0)
