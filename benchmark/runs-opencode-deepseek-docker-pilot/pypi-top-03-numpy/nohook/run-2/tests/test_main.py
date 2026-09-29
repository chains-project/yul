import numpy as np

from numcompute.main import build_system, solve_system


def test_build_system_shapes():
    a, b = build_system(5, seed=1)
    assert a.shape == (5, 5)
    assert b.shape == (5,)


def test_build_system_rejects_bad_size():
    import pytest

    with pytest.raises(ValueError):
        build_system(0)


def test_solve_system_recovers_known_solution():
    a, _ = build_system(8, seed=3)
    expected = np.arange(8, dtype=np.float64)
    b = a @ expected
    x = solve_system(a, b)
    np.testing.assert_allclose(x, expected, rtol=1e-10, atol=1e-10)


def test_solve_system_rejects_non_square():
    import pytest

    with pytest.raises(ValueError):
        solve_system(np.ones((2, 3)), np.ones(2))
