import numpy as np
import pytest

from matrixlab import (
    eigen_decomposition,
    matmul_blocked,
    matvec,
    solve_linear_system,
)


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(1234)


def test_matmul_blocked_matches_numpy(rng: np.random.Generator) -> None:
    a = rng.standard_normal((130, 90))
    b = rng.standard_normal((90, 110))
    np.testing.assert_allclose(matmul_blocked(a, b), a @ b, rtol=1e-10, atol=1e-10)


def test_matmul_blocked_respects_block_size(rng: np.random.Generator) -> None:
    a = rng.standard_normal((40, 40))
    b = rng.standard_normal((40, 40))
    np.testing.assert_allclose(matmul_blocked(a, b, block_size=7), a @ b, rtol=1e-10, atol=1e-10)


def test_matmul_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="shape mismatch"):
        matmul_blocked(np.ones((2, 3)), np.ones((2, 2)))


def test_matvec(rng: np.random.Generator) -> None:
    a = rng.standard_normal((5, 4))
    v = rng.standard_normal(4)
    np.testing.assert_allclose(matvec(a, v), a @ v)


def test_solve_linear_system(rng: np.random.Generator) -> None:
    a = rng.standard_normal((6, 6)) + 6 * np.eye(6)
    b = rng.standard_normal(6)
    x = solve_linear_system(a, b)
    np.testing.assert_allclose(a @ x, b, rtol=1e-10, atol=1e-10)


def test_solve_requires_square() -> None:
    with pytest.raises(ValueError, match="square"):
        solve_linear_system(np.ones((2, 3)), np.ones(2))


def test_eigen_decomposition_symmetric(rng: np.random.Generator) -> None:
    a = rng.standard_normal((8, 8))
    a = a + a.T
    values, vectors = eigen_decomposition(a)
    assert np.all(np.diff(values) >= 0)
    np.testing.assert_allclose(a @ vectors, vectors * values, rtol=1e-9, atol=1e-9)
