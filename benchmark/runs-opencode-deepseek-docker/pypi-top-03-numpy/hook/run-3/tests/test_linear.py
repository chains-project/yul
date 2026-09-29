import numpy as np
import pytest

from numcompute.linear import (
    batched_matmul,
    condition_number,
    eigenvalues,
    matmul,
    solve_linear_system,
)


@pytest.fixture
def rng():
    return np.random.default_rng(42)


def test_matmul_matches_numpy(rng):
    a = rng.standard_normal((8, 5))
    b = rng.standard_normal((5, 3))
    np.testing.assert_allclose(matmul(a, b), a @ b)


def test_matmul_rejects_misaligned_shapes():
    with pytest.raises(ValueError):
        matmul(np.ones((3, 4)), np.ones((3, 4)))


def test_matmul_rejects_non_2d():
    with pytest.raises(ValueError):
        matmul(np.ones(3), np.ones(3))


def test_batched_matmul(rng):
    a = rng.standard_normal((10, 4, 6))
    b = rng.standard_normal((10, 6, 2))
    np.testing.assert_allclose(batched_matmul(a, b), np.matmul(a, b))


def test_solve_linear_system_recovers_solution(rng):
    a = rng.standard_normal((6, 6)) + 6 * np.eye(6)
    truth = rng.standard_normal(6)
    x = solve_linear_system(a, a @ truth)
    np.testing.assert_allclose(x, truth, rtol=1e-10, atol=1e-10)


def test_solve_requires_square():
    with pytest.raises(ValueError):
        solve_linear_system(np.ones((3, 4)), np.ones(3))


def test_eigenvalues_symmetric_are_real(rng):
    m = rng.standard_normal((5, 5))
    sym = m + m.T
    vals = eigenvalues(sym)
    assert np.isrealobj(vals)
    np.testing.assert_allclose(np.sort(vals), np.sort(np.linalg.eigvalsh(sym)))


def test_condition_number_identity_is_one():
    assert condition_number(np.eye(4)) == pytest.approx(1.0)
