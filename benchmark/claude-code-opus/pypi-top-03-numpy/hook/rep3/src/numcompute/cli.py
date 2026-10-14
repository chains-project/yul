"""Command-line entry point."""

import argparse
import time

import numpy as np

from numcompute.linalg import solve_system, spectral_summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--size", type=int, default=2000, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    a = rng.standard_normal((args.size, args.size))
    b = rng.standard_normal(args.size)

    t0 = time.perf_counter()
    x = solve_system(a, b)
    elapsed = time.perf_counter() - t0

    residual = np.linalg.norm(a @ x - b) / np.linalg.norm(b)
    print(f"solved {args.size}x{args.size} in {elapsed:.3f}s, relative residual {residual:.2e}")
    for key, value in spectral_summary(a).items():
        print(f"  {key}: {value:.4g}")
