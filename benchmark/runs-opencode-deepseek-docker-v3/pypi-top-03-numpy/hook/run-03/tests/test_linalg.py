from __future__ import annotations

import numpy as np
import pytest

from numcompute import (
    as_matrix,
    condition_number,
    eigenvalues,
    matmul,
    matrix_power,
    random_spd,
    singular_values,
    solve,
)


def test_as_matrix_rejects_non_2d() -> None:
    with pytest.raises(ValueError, match="2-D"):
        as_matrix([1.0, 2.0, 3.0])


def test_as_matrix_rejects_non_square_when_required() -> None:
    with pytest.raises(ValueError, match="square"):
        as_matrix(np.ones((2, 3)), square=True)


def test_matmul_matches_numpy() -> None:
    rng = np.random.default_rng(1)
    a = rng.standard_normal((4, 5))
    b = rng.standard_normal((5, 3))
    np.testing.assert_allclose(matmul(a, b), a @ b)


def test_matmul_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="inner dimensions"):
        matmul(np.ones((2, 3)), np.ones((2, 3)))


def test_solve_recovers_known_solution() -> None:
    a = random_spd(6, seed=42)
    x = np.arange(6, dtype=np.float64)
    b = a @ x
    np.testing.assert_allclose(solve(a, b), x, atol=1e-10)


def test_eigenvalues_of_symmetric_matrix_are_real() -> None:
    a = random_spd(5, seed=7)
    vals = eigenvalues(a)
    assert np.all(np.isreal(vals))
    assert np.all(vals > 0)


def test_singular_values_are_descending_and_nonnegative() -> None:
    rng = np.random.default_rng(3)
    sv = singular_values(rng.standard_normal((8, 4)))
    assert np.all(sv >= 0)
    assert np.all(np.diff(sv) <= 0)


def test_condition_number_of_identity_is_one() -> None:
    assert condition_number(np.eye(4)) == pytest.approx(1.0)


def test_matrix_power() -> None:
    a = np.array([[1.0, 1.0], [0.0, 1.0]])
    np.testing.assert_allclose(matrix_power(a, 3), np.array([[1.0, 3.0], [0.0, 1.0]]))
