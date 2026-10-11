"""Command-line entry point for matcomp.

Examples:
    python -m matcomp bench --size 2048
    python -m matcomp dominant --size 128
"""

from __future__ import annotations

import argparse
import time

import numpy as np

from matcomp.core import gram_matrix, matmul, power_iteration


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="matcomp", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    bench = sub.add_parser("bench", help="time core matrix operations")
    bench.add_argument("--size", type=int, default=1024, help="matrix size")
    bench.add_argument("--repeat", type=int, default=3, help="timed runs")

    dom = sub.add_parser("dominant", help="estimate dominant eigenvalue/vector")
    dom.add_argument("--size", type=int, default=128, help="matrix size")
    dom.add_argument("--iterations", type=int, default=1000)

    return parser


def _time(fn, repeat: int) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def cmd_bench(args: argparse.Namespace) -> int:
    rng = np.random.default_rng(0)
    a = rng.standard_normal((args.size, args.size))
    b = rng.standard_normal((args.size, args.size))

    matmul_time = _time(lambda: matmul(a, b), args.repeat)
    gram_time = _time(lambda: gram_matrix(a), args.repeat)

    flops = 2 * args.size**3
    rate = flops / matmul_time / 1e9
    print(f"size            : {args.size}x{args.size}")
    print(f"matmul          : {matmul_time * 1e3:9.2f} ms  ({rate:7.2f} GFLOP/s)")
    print(f"gram (A.T @ A)  : {gram_time * 1e3:9.2f} ms")
    return 0


def cmd_dominant(args: argparse.Namespace) -> int:
    rng = np.random.default_rng(0)
    a = rng.standard_normal((args.size, args.size))
    a = a + a.T  # symmetric => real, well-separated spectrum

    eigenvalue, _ = power_iteration(a, iterations=args.iterations)
    spectrum = np.linalg.eigvalsh(a)
    reference = float(spectrum[np.argmax(np.abs(spectrum))])
    print(f"power iteration : {eigenvalue:.10f}  (largest magnitude)")
    print(f"numpy reference : {reference:.10f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "bench":
        return cmd_bench(args)
    return cmd_dominant(args)


if __name__ == "__main__":
    raise SystemExit(main())
