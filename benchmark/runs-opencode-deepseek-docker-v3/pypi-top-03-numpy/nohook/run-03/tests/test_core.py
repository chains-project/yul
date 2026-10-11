import numpy as np
import pytest

from numcompute import core


def test_matmul_identity() -> None:
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    identity = np.eye(2)
    np.testing.assert_allclose(core.matmul(a, identity), a)


def test_solve_recovers_vector() -> None:
    a = np.array([[3.0, 1.0], [1.0, 2.0]])
    b = np.array([9.0, 8.0])
    np.testing.assert_allclose(core.matmul(a, core.solve(a, b)), b)


def test_determinant() -> None:
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert core.determinant(a) == pytest.approx(-2.0)


def test_inverse_roundtrip() -> None:
    a = np.array([[2.0, 0.0], [0.0, 4.0]])
    np.testing.assert_allclose(core.matmul(a, core.inverse(a)), np.eye(2))


def test_eigvals_diagonal() -> None:
    a = np.diag([2.0, 3.0, 4.0])
    np.testing.assert_allclose(np.sort(core.eigvals(a).real), [2.0, 3.0, 4.0])
