"""Timing harness for the heavy numerical routines."""

from __future__ import annotations

import argparse
import time

from . import core


def _timed(fn, *args, repeats: int = 3) -> float:
    """Return the best wall-clock time (seconds) over ``repeats`` runs."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - start)
    return best


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="matrix-compute",
        description="Run timing benchmarks for dense matrix operations.",
    )
    parser.add_argument("--size", type=int, default=2048, help="matrix dimension")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed")
    parser.add_argument("--repeats", type=int, default=3, help="runs per operation")
    args = parser.parse_args(argv)

    n = args.size
    a = core.random_matrix(n, n, seed=args.seed)
    b = core.random_matrix(n, n, seed=args.seed + 1)

    print(f"Benchmarking {n}x{n} matrices (best of {args.repeats})")

    mm = _timed(core.matmul, a, b, repeats=args.repeats)
    print(f"  matmul            {mm:.4f}s")

    if n <= 4096:
        solve = _timed(core.solve_linear, a, b, repeats=args.repeats)
        print(f"  solve_linear      {solve:.4f}s")

    svd = _timed(core.singular_values, a, repeats=args.repeats)
    print(f"  singular_values   {svd:.4f}s")


if __name__ == "__main__":
    main()
