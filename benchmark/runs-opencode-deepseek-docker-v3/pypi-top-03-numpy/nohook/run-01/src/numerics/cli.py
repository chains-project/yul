"""Command-line entry point for a small matrix-computation demo."""

from __future__ import annotations

import argparse
import time

import numpy as np

from numerics.core import conditioning, eigenvalues, matmul, solve


def _timed(label: str, fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    print(f"{label:<24} {elapsed * 1e3:9.2f} ms")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--size", type=int, default=2048, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    args = parser.parse_args(argv)

    n = args.size
    rng = np.random.default_rng(args.seed)
    a = rng.standard_normal((n, n))
    b = rng.standard_normal((n, n))
    print(f"dtype={a.dtype} shape={a.shape}")

    _timed("matmul", matmul, a, b)
    _timed("solve", solve, a, np.ones(n))
    _timed("eigenvalues (symmetric)", eigenvalues, a + a.T)
    print(f"{'condition number':<24} {conditioning(a):9.3e}")


if __name__ == "__main__":
    main()
