"""Command-line entry point for heavy numerical array and matrix computations."""

from __future__ import annotations

import argparse
import time

import numpy as np


def random_spd_matrix(size: int, rng: np.random.Generator) -> np.ndarray:
    """Return a random symmetric positive-definite matrix of shape (size, size)."""
    a = rng.standard_normal((size, size))
    return a @ a.T + size * np.eye(size)


def power_iteration(
    matrix: np.ndarray,
    iterations: int = 100_000,
    tol: float = 1e-10,
) -> tuple[float, np.ndarray]:
    """Estimate the dominant eigenvalue and eigenvector via power iteration.

    Stops once the relative residual ``||A v - lambda v|| / |lambda|`` falls
    below ``tol``, which converges far more reliably than watching the
    Rayleigh quotient alone.
    """
    size = matrix.shape[0]
    vector = np.ones(size) / np.sqrt(size)
    eigenvalue = 0.0

    for _ in range(iterations):
        product = matrix @ vector
        eigenvalue = float(vector @ product)
        residual = np.linalg.norm(product - eigenvalue * vector)
        if residual <= tol * abs(eigenvalue):
            return eigenvalue, vector
        vector = product / np.linalg.norm(product)

    return eigenvalue, vector


def benchmark(size: int, seed: int) -> dict[str, float]:
    """Time matrix multiplication and eigendecomposition for a random problem."""
    rng = np.random.default_rng(seed)
    left = random_spd_matrix(size, rng)
    right = random_spd_matrix(size, rng)

    start = time.perf_counter()
    product = left @ right
    matmul_seconds = time.perf_counter() - start

    start = time.perf_counter()
    eigenvalues = np.linalg.eigvalsh(product)
    eigendecomp_seconds = time.perf_counter() - start

    return {
        "matmul_seconds": matmul_seconds,
        "eigendecomp_seconds": eigendecomp_seconds,
        "largest_eigenvalue": float(eigenvalues[-1]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark heavy numerical array and matrix computations.",
    )
    parser.add_argument("-n", "--size", type=int, default=1024, help="matrix dimension")
    parser.add_argument("-s", "--seed", type=int, default=0, help="random seed")
    args = parser.parse_args()

    results = benchmark(args.size, args.seed)
    print(f"matrix size        : {args.size} x {args.size}")
    print(f"matmul             : {results['matmul_seconds']:.4f} s")
    print(f"eigendecomposition : {results['eigendecomp_seconds']:.4f} s")
    print(f"largest eigenvalue : {results['largest_eigenvalue']:.6f}")


if __name__ == "__main__":
    main()
