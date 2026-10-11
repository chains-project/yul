"""Command-line entry point for benchmarking matrix computations."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from time import perf_counter

from numcompute import condition_number, eigenvalues, matmul, random_spd, solve


def _time(label: str, func: Callable[[], object]) -> None:
    start = perf_counter()
    result = func()
    elapsed = perf_counter() - start
    size = getattr(result, "shape", None) or getattr(result, "size", "")
    print(f"{label:<24} {elapsed * 1e3:9.3f} ms   {size}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="numcompute", description=__doc__)
    parser.add_argument("-n", "--size", type=int, default=1024, help="matrix size")
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    args = parser.parse_args(argv)

    n = args.size
    a = random_spd(n, seed=args.seed)
    b = random_spd(n, seed=args.seed + 1)

    print(f"Benchmarking {n}x{n} float64 matrices\n")
    _time("matmul", lambda: matmul(a, b))
    _time("solve", lambda: solve(a, b))
    _time("eigenvalues", lambda: eigenvalues(a))
    _time("condition_number", lambda: condition_number(a))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
