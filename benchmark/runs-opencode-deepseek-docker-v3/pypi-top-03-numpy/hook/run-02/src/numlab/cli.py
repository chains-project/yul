"""Command-line entry point for the numlab numerical routines."""

from __future__ import annotations

import argparse
import time

import numpy as np

from numlab import linalg


def _run(args: argparse.Namespace) -> None:
    n = args.size
    a = linalg.random_spd_matrix(n, seed=args.seed)

    start = time.perf_counter()
    if args.operation == "multiply":
        result = linalg.matrix_multiply(a, a)
        summary = float(result.sum())
    elif args.operation == "solve":
        b = a @ np.ones(n)
        result = linalg.solve_linear_system(a, b)
        summary = float(result.sum())
    elif args.operation == "eigen":
        result = linalg.eigenvalues(a)
        summary = float(result.real.sum())
    elif args.operation == "svd":
        result = linalg.singular_values(a)
        summary = float(result.sum())
    elif args.operation == "cholesky":
        result = linalg.cholesky(a)
        summary = float(result.sum())
    else:
        eigenvalue, _ = linalg.power_iteration(a)
        summary = eigenvalue
    elapsed = time.perf_counter() - start

    print(f"{args.operation} n={n}: checksum={summary:.6f} time={elapsed:.4f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Heavy numerical array and matrix computations.")
    parser.add_argument(
        "operation",
        choices=["multiply", "solve", "eigen", "svd", "cholesky", "power"],
        help="Matrix operation to benchmark.",
    )
    parser.add_argument("-n", "--size", type=int, default=512, help="Matrix dimension.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed.")
    _run(parser.parse_args())
