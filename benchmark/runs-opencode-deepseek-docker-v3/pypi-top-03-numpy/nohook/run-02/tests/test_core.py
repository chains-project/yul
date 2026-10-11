import numpy as np
from numpy.testing import assert_allclose

from matrix_compute import core


def test_matmul_matches_numpy():
    a = core.random_matrix(4, 5, seed=1)
    b = core.random_matrix(5, 3, seed=2)
    assert_allclose(core.matmul(a, b), a @ b)


def test_solve_linear_square_system():
    a = core.random_matrix(5, 5, seed=3)
    b = core.random_matrix(5, 2, seed=4)
    x = core.solve_linear(a, b)
    assert_allclose(a @ x, b, atol=1e-10)


def test_solve_linear_least_squares():
    a = core.random_matrix(6, 4, seed=5)
    b = core.random_matrix(6, 1, seed=6)
    x = core.solve_linear(a, b)
    expected = np.linalg.lstsq(a, b, rcond=None)[0]
    assert_allclose(x, expected, atol=1e-10)


def test_eigenvalues_of_symmetric_matrix_are_real():
    a = core.random_matrix(5, 5, seed=7)
    a = a + a.T
    vals = core.eigenvalues(a)
    assert_allclose(vals.imag, 0.0, atol=1e-10)


def test_singular_values_match_numpy():
    a = core.random_matrix(5, 3, seed=8)
    expected = np.linalg.svd(a, compute_uv=False)
    assert_allclose(core.singular_values(a), expected)


def test_condition_number_of_scaled_identity_is_one():
    assert core.condition_number(np.eye(3) * 2) == 1.0
