"""Command-line entry point."""

import argparse
import time

import numpy as np

from numcompute.linalg import solve_system, spectral_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run matrix computations on random data.")
    parser.add_argument("-n", "--size", type=int, default=1000, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    m = rng.standard_normal((args.size, args.size))
    a = m @ m.T + args.size * np.eye(args.size)  # symmetric positive definite
    b = rng.standard_normal(args.size)

    t0 = time.perf_counter()
    x = solve_system(a, b)
    elapsed = time.perf_counter() - t0

    print(f"n={args.size}  solve: {elapsed:.3f}s  residual: {np.linalg.norm(a @ x - b):.2e}")
    print(spectral_summary(a))


if __name__ == "__main__":
    main()
