"""Command-line entry point."""

import argparse
import time

import numpy as np

from numcompute.linalg import random_spd, relative_residual, solve_spd


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a dense SPD solve benchmark.")
    parser.add_argument("-n", "--size", type=int, default=2000, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed")
    args = parser.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    a = random_spd(args.size, rng)
    b = rng.standard_normal(args.size)

    start = time.perf_counter()
    x = solve_spd(a, b)
    elapsed = time.perf_counter() - start

    print(f"n={args.size}  solve={elapsed:.3f}s  residual={relative_residual(a, x, b):.2e}")
