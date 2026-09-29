"""Command-line entry point for running matrix-computation workloads."""

from __future__ import annotations

import argparse
import time

import numpy as np

from .linear import condition_number, eigenvalues, matmul, solve_linear_system


def _time(label: str, fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    print(f"{label:<22} {elapsed * 1e3:8.2f} ms")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="numcompute",
        description="Run dense numerical array/matrix workloads.",
    )
    parser.add_argument(
        "-n", "--size", type=int, default=2048,
        help="matrix dimension (default: 2048)",
    )
    parser.add_argument(
        "--seed", type=int, default=0, help="random seed (default: 0)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="report numerical diagnostics after the workload",
    )
    args = parser.parse_args(argv)

    if args.size < 1:
        parser.error("--size must be a positive integer")

    rng = np.random.default_rng(args.seed)
    n = args.size
    a = rng.standard_normal((n, n))
    b = rng.standard_normal((n, n))

    print(f"Dense matrix workload: n={n}, dtype=float64")
    product = _time("matmul", matmul, a, b)
    _time("solve", solve_linear_system, a, np.eye(n))
    _time("eigenvalues", eigenvalues, a)

    if args.check:
        residual = np.linalg.norm(product - a @ b)
        print(f"matmul residual        {residual:.3e}")
        print(f"condition number       {condition_number(a):.3e}")

    return 0
