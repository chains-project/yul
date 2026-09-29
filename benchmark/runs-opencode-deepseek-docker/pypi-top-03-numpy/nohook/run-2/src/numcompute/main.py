"""Matrix computation entry point.

Demonstrates the core workflow: build an array, then solve a linear system
``A @ x = b`` using the chosen NumPy backend.
"""

from __future__ import annotations

import argparse

import numpy as np
from numpy.typing import NDArray

Matrix = NDArray[np.float64]
Vector = NDArray[np.float64]


def build_system(n: int, *, seed: int = 0) -> tuple[Matrix, Vector]:
    """Return a well-conditioned ``n x n`` matrix ``A`` and right-hand side ``b``."""
    if n <= 0:
        raise ValueError("n must be a positive integer")

    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n, n))
    a += n * np.eye(n)
    b = rng.standard_normal(n)
    return a, b


def solve_system(a: Matrix, b: Vector) -> Vector:
    """Solve ``a @ x = b`` and return the solution vector ``x``."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("a must be a square 2-D array")
    if b.shape != (a.shape[0],):
        raise ValueError("b must be a 1-D array matching a's dimension")

    return np.linalg.solve(a, b)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solve a dense linear system.")
    parser.add_argument("-n", type=int, default=1000, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    parser.add_argument(
        "--check", action="store_true", help="report the residual norm"
    )
    args = parser.parse_args(argv)

    a, b = build_system(args.n, seed=args.seed)
    x = solve_system(a, b)

    print(f"shape: {a.shape}  solution[:3]={np.round(x[:3], 6)}")
    if args.check:
        residual = np.linalg.norm(a @ x - b)
        print(f"residual ||Ax - b|| = {residual:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
