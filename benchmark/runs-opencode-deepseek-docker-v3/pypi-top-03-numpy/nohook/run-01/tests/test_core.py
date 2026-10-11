from __future__ import annotations

import numpy as np
import pytest

from numerics import eigenvalues, matmul, solve


@pytest.fixture()
def rng() -> np.random.Generator:
    return np.random.default_rng(42)


def test_matmul_matches_numpy(rng: np.random.Generator) -> None:
    a = rng.standard_normal((16, 24))
    b = rng.standard_normal((24, 8))
    np.testing.assert_allclose(matmul(a, b), a @ b)


def test_solve_reconstructs_rhs(rng: np.random.Generator) -> None:
    a = rng.standard_normal((32, 32)) + 32 * np.eye(32)
    b = rng.standard_normal(32)
    x = solve(a, b)
    np.testing.assert_allclose(a @ x, b, rtol=1e-10, atol=1e-10)


def test_eigenvalues_are_sorted_real(rng: np.random.Generator) -> None:
    m = rng.standard_normal((24, 24))
    sym = m + m.T
    values = eigenvalues(sym)
    assert np.isrealobj(values)
    assert np.all(np.diff(values) >= 0)
    np.testing.assert_allclose(values, np.linalg.eigvalsh(sym))
