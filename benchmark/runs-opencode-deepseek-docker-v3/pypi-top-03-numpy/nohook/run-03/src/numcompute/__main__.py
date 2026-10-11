"""Command line entrypoint for numcompute."""

from __future__ import annotations

import argparse

import numpy as np

from numcompute import core


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="numcompute", description="Matrix computation demo.")
    parser.add_argument("-n", "--size", type=int, default=4, help="size of the random matrix")
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rng = np.random.default_rng(args.seed)
    a = rng.standard_normal((args.size, args.size))
    b = rng.standard_normal(args.size)

    x = core.solve(a, b)
    print(f"matrix shape : {a.shape}")
    print(f"determinant  : {core.determinant(a):.6f}")
    print(f"solution norm: {float(np.linalg.norm(x)):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
