"""Command-line entry point demonstrating the numerical kernels."""

from __future__ import annotations

import argparse
import time

import numpy as np

from numcompute.core import covariance, first_eigenpair, matrix_multiply, monte_carlo_pi


def _timed(label: str, func, *args, **kwargs):  # type: ignore[no-untyped-def]
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return label, result, elapsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="numcompute", description=__doc__)
    parser.add_argument("--size", type=int, default=2000, help="matrix/array dimension")
    parser.add_argument("--samples", type=int, default=5_000_000, help="Monte Carlo samples")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    args = parser.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    a = rng.standard_normal((args.size, args.size))
    b = rng.standard_normal((args.size, args.size))
    data = rng.standard_normal((args.size, 8))

    print(f"numpy {np.__version__} | size={args.size} | samples={args.samples:,}\n")

    label, product, elapsed = _timed("matrix multiply", matrix_multiply, a, b)
    print(f"{label:<18} {elapsed:7.3f}s  shape={product.shape}")

    label, cov, elapsed = _timed("covariance", covariance, data)
    print(f"{label:<18} {elapsed:7.3f}s  shape={cov.shape}")

    symmetric = a + a.T
    label, (value, _), elapsed = _timed("eigenpair", first_eigenpair, symmetric)
    print(f"{label:<18} {elapsed:7.3f}s  lambda_max={value:.6f}")

    label, pi, elapsed = _timed("monte carlo pi", monte_carlo_pi, args.samples, seed=args.seed)
    print(f"{label:<18} {elapsed:7.3f}s  pi~{pi:.6f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
