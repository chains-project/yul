import numpy as np

from numlab import linalg


def test_matrix_multiply_matches_reference() -> None:
    a = linalg.random_spd_matrix(8, seed=1)
    b = linalg.random_spd_matrix(8, seed=2)
    np.testing.assert_allclose(linalg.matrix_multiply(a, b), a @ b)


def test_solve_linear_system() -> None:
    a = linalg.random_spd_matrix(16, seed=3)
    x = np.arange(16, dtype=np.float64)
    b = a @ x
    np.testing.assert_allclose(linalg.solve_linear_system(a, b), x, rtol=1e-9, atol=1e-9)


def test_eigenvalues_of_spd_are_positive() -> None:
    a = linalg.random_spd_matrix(32, seed=4)
    values = linalg.eigenvalues(a)
    assert np.all(values > 0.0)


def test_singular_values_sorted_descending() -> None:
    a = linalg.random_spd_matrix(24, seed=5)
    values = linalg.singular_values(a)
    assert np.all(np.diff(values) <= 0.0)


def test_cholesky_reconstructs_matrix() -> None:
    a = linalg.random_spd_matrix(20, seed=6)
    lower = linalg.cholesky(a)
    np.testing.assert_allclose(lower @ lower.T, a, rtol=1e-9)


def test_power_iteration_finds_dominant_eigenvalue() -> None:
    a = linalg.random_spd_matrix(30, seed=7)
    estimate, vector = linalg.power_iteration(a)
    expected = np.linalg.eigvalsh(a)[-1]
    assert abs(estimate - expected) < 1e-6
    np.testing.assert_allclose(a @ vector, estimate * vector, atol=1e-3)
