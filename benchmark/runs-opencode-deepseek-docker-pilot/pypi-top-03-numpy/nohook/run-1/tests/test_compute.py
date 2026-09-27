import numpy as np

from numerical.compute import (
    eigen,
    matmul,
    matrix_power,
    solve_linear_system,
    svd,
)


def test_matmul() -> None:
    a = [[1.0, 2.0], [3.0, 4.0]]
    b = [[5.0, 6.0], [7.0, 8.0]]
    np.testing.assert_allclose(matmul(a, b), [[19.0, 22.0], [43.0, 50.0]])


def test_matrix_power() -> None:
    a = np.eye(3)
    np.testing.assert_allclose(matrix_power(a, 5), np.eye(3))


def test_solve_linear_system() -> None:
    a = [[3.0, 1.0], [1.0, 2.0]]
    b = [9.0, 8.0]
    x = solve_linear_system(a, b)
    np.testing.assert_allclose(matmul(a, x), b)


def test_svd_reconstruction() -> None:
    rng = np.random.default_rng(0)
    a = rng.standard_normal((5, 3))
    u, s, vt = svd(a)
    np.testing.assert_allclose(u @ np.diag(s) @ vt, a, atol=1e-10)


def test_eigen() -> None:
    a = np.diag([1.0, 2.0, 3.0])
    values, vectors = eigen(a)
    np.testing.assert_allclose(sorted(values), [1.0, 2.0, 3.0])
    np.testing.assert_allclose(np.abs(vectors), np.eye(3), atol=1e-12)
