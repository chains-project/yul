from __future__ import annotations

import numpy as np
import pytest

from matrixlab.main import benchmark, power_iteration, random_spd_matrix


def test_random_spd_matrix_is_symmetric_positive_definite() -> None:
    rng = np.random.default_rng(0)
    matrix = random_spd_matrix(32, rng)

    assert np.allclose(matrix, matrix.T)
    assert np.all(np.linalg.eigvalsh(matrix) > 0.0)


def test_power_iteration_matches_numpy() -> None:
    rng = np.random.default_rng(1)
    matrix = random_spd_matrix(64, rng)

    eigenvalue, eigenvector = power_iteration(matrix)
    expected = float(np.linalg.eigvalsh(matrix)[-1])

    assert eigenvalue == pytest.approx(expected, rel=1e-6)
    assert np.allclose(matrix @ eigenvector, eigenvalue * eigenvector, atol=1e-5)


def test_benchmark_returns_finite_metrics() -> None:
    results = benchmark(size=64, seed=2)

    assert results["matmul_seconds"] >= 0.0
    assert results["eigendecomp_seconds"] >= 0.0
    assert np.isfinite(results["largest_eigenvalue"])
