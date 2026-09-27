from __future__ import annotations

import argparse
import time

import numpy as np

from numerical.compute import matmul, svd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run heavy numerical array/matrix computations."
    )
    parser.add_argument(
        "--size",
        type=int,
        default=1000,
        help="side length of the square matrices to use (default: 1000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="random seed for reproducibility (default: 0)",
    )
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    a = rng.standard_normal((args.size, args.size))
    b = rng.standard_normal((args.size, args.size))

    t0 = time.perf_counter()
    c = matmul(a, b)
    t1 = time.perf_counter()
    print(f"matmul {args.size}x{args.size}: {t1 - t0:.3f}s")

    t0 = time.perf_counter()
    u, s, vt = svd(a)
    t1 = time.perf_counter()
    print(f"svd    {args.size}x{args.size}: {t1 - t0:.3f}s")
    print(f"result shape: {c.shape}, top singular value: {s[0]:.6f}")


if __name__ == "__main__":
    main()
