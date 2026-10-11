import numpy as np
import pytest

from matcomp import gram_matrix, matmul, power_iteration, solve


def test_matmul_matches_numpy() -> None:
    rng = np.random.default_rng(1)
    a = rng.standard_normal((5, 3))
    b = rng.standard_normal((3, 4))
    np.testing.assert_allclose(matmul(a, b), a @ b)


def test_matmul_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="shape mismatch"):
        matmul(np.ones((2, 3)), np.ones((2, 3)))


def test_gram_is_symmetric_psd() -> None:
    rng = np.random.default_rng(2)
    a = rng.standard_normal((7, 4))
    g = gram_matrix(a)
    np.testing.assert_allclose(g, g.T)
    assert np.all(np.linalg.eigvalsh(g) > -1e-12)


def test_solve_recovers_solution() -> None:
    rng = np.random.default_rng(3)
    a = rng.standard_normal((6, 6)) + 6 * np.eye(6)
    x = rng.standard_normal(6)
    np.testing.assert_allclose(solve(a, a @ x), x)


def test_power_iteration_finds_dominant_eigenvalue() -> None:
    rng = np.random.default_rng(4)
    a = rng.standard_normal((8, 8))
    a = a + a.T
    eigenvalue, vector = power_iteration(a)
    reference = np.linalg.eigvalsh(a)[-1]
    np.testing.assert_allclose(eigenvalue, reference, rtol=1e-6)
    np.testing.assert_allclose(a @ vector, eigenvalue * vector, atol=1e-6)


def test_power_iteration_rejects_non_square() -> None:
    with pytest.raises(ValueError, match="square"):
        power_iteration(np.ones((2, 3)))
