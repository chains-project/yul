"""Command-line entry point."""

import time

import numpy as np

from numcompute.linalg import solve_linear_system


def main() -> None:
    rng = np.random.default_rng(seed=0)
    n = 2000
    a = rng.standard_normal((n, n))
    b = rng.standard_normal(n)

    start = time.perf_counter()
    x = solve_linear_system(a, b)
    elapsed = time.perf_counter() - start

    residual = np.linalg.norm(a @ x - b)
    print(f"Solved {n}x{n} system in {elapsed:.3f}s (residual {residual:.2e})")


if __name__ == "__main__":
    main()
