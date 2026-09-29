from __future__ import annotations

import argparse
import time

import numpy as np

from matrixlab import __version__
from matrixlab.core import eigen_decomposition, matmul_blocked, solve_linear_system


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="matrixlab", description="Matrix computation benchmarks.")
    parser.add_argument("--version", action="version", version=f"matrixlab {__version__}")
    parser.add_argument("--size", type=int, default=512, help="matrix dimension (default: 512)")
    parser.add_argument(
        "--op",
        choices=["matmul", "solve", "eig"],
        default="matmul",
        help="operation to run (default: matmul)",
    )
    parser.add_argument("--seed", type=int, default=0, help="random seed (default: 0)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    rng = np.random.default_rng(args.seed)
    n = args.size
    a = rng.standard_normal((n, n))

    start = time.perf_counter()
    if args.op == "matmul":
        result = matmul_blocked(a, a)
        detail = f"trace={np.trace(result):.4f}"
    elif args.op == "solve":
        b = rng.standard_normal(n)
        x = solve_linear_system(a, b)
        detail = f"residual={np.linalg.norm(a @ x - b):.3e}"
    else:
        values, _ = eigen_decomposition(a + a.T)
        detail = f"lambda_max={values[-1]:.4f}"
    elapsed = time.perf_counter() - start

    print(f"{args.op} n={n} time={elapsed:.4f}s {detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
