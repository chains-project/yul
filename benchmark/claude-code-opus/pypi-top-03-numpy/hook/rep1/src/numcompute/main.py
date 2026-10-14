"""Command-line entry point."""

import argparse
import time

import numpy as np

from numcompute.linalg import random_spd, solve_spd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--size", type=int, default=2000, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    a = random_spd(args.size, rng)
    b = rng.standard_normal(args.size)

    start = time.perf_counter()
    x = solve_spd(a, b)
    elapsed = time.perf_counter() - start

    residual = np.linalg.norm(a @ x - b) / np.linalg.norm(b)
    print(f"n={args.size}  solve time={elapsed:.3f}s  relative residual={residual:.2e}")


if __name__ == "__main__":
    main()
