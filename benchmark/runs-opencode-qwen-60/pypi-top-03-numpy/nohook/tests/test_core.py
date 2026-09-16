"""Tests for numerical array and matrix computations."""

import numpy as np
import pytest

from numerical_array_tools.core import (
    condition_number,
    eigenvalues,
    lu_decomposition,
    matmul,
    matrix_power,
    solve_system,
    svd,
)


class TestMatmul:
    def test_square_matrix_multiplication(self):
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        result = matmul(a, b)
        expected = np.array([[19, 22], [43, 50]])
        np.testing.assert_array_equal(result, expected)

    def test_batch_multiplication(self):
        a = np.random.randn(10, 20)
        b = np.random.randn(20, 5)
        result = matmul(a, b)
        assert result.shape == (10, 5)


class TestEigenvalues:
    def test_identity_eigenvalues(self):
        a = np.eye(3)
        vals = eigenvalues(a)
        np.testing.assert_array_almost_equal(vals, [1.0, 1.0, 1.0])

    def test_symmetric_eigenvalues(self):
        a = np.array([[2, 1], [1, 2]])
        vals = eigenvalues(a)
        np.testing.assert_array_almost_equal(vals, [3.0, 1.0])

    def test_top_k(self):
        a = np.array([[4, 0], [0, 3], [0, 0, 2]])
        vals = eigenvalues(a, k=2)
        np.testing.assert_array_almost_equal(vals, [4.0, 3.0])


class TestSVD:
    def test_diagonal_matrix(self):
        a = np.diag([3, 2, 1])
        u, s, vt = svd(a, compute_uv=True)
        np.testing.assert_array_almost_equal(s, [3, 2, 1])

    def test_singular_values_only(self):
        a = np.array([[1, 0], [0, 2]])
        s = svd(a, compute_uv=False)
        np.testing.assert_array_almost_equal(s, [2, 1])


class TestLU:
    def test_decomposition_correctness(self):
        a = np.array([[2, 1, 1], [4, 3, 3], [8, 7, 9]])
        p, l, u = lu_decomposition(a)
        np.testing.assert_array_almost_equal(p @ a, l @ u)

    def test_permutation_matrix(self):
        a = np.array([[1, 2], [3, 4]])
        p, _, _ = lu_decomposition(a)
        # P should be a permutation matrix
        np.testing.assert_array_equal(np.sort(p, axis=1), np.ones_like(p))


class TestConditionNumber:
    def test_identity(self):
        eps = np.finfo(float).eps
        assert abs(condition_number(np.eye(3)) - 1.0) < eps


class TestMatrixPower:
    def test_identity_power(self):
        a = np.eye(3)
        result = matrix_power(a, 100)
        np.testing.assert_array_almost_equal(result, a)

    def test_squared(self):
        a = np.array([[1, 1], [0, 1]])
        result = matrix_power(a, 2)
        expected = np.array([[1, 2], [0, 1]])
        np.testing.assert_array_equal(result, expected)


class TestSolveSystem:
    def test_linear_system(self):
        a = np.array([[2, 1], [1, -1]])
        b = np.array([5, 0])
        x = solve_system(a, b)
        np.testing.assert_array_almost_equal(x, [2.0, 1.0])

    def test_multi_rhs(self):
        a = np.array([[1, 0], [0, 1]])
        b = np.array([[1, 2], [3, 4]])
        x = solve_system(a, b)
        np.testing.assert_array_almost_equal(x, b)