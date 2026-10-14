import numpy as np
import pytest

from numcompute import solve_linear_system


def test_solve_matches_known_solution():
    rng = np.random.default_rng(seed=42)
    a = rng.standard_normal((50, 50))
    x_true = rng.standard_normal(50)
    x = solve_linear_system(a, a @ x_true)
    np.testing.assert_allclose(x, x_true, rtol=1e-8)


def test_solve_rejects_non_square():
    with pytest.raises(ValueError, match="square"):
        solve_linear_system(np.ones((3, 2)), np.ones(3))
