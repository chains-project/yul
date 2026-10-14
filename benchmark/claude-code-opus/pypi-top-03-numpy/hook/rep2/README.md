# numcompute

Numerical array and matrix computations built on NumPy and SciPy.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```sh
uv sync
```

## Usage

```sh
uv run numcompute
```

## Development

```sh
uv run pytest            # run tests
uv run ruff check .      # lint
uv run ruff format .     # format
```

## Performance notes

- Vectorize with NumPy operations instead of Python loops.
- Prefer `scipy.linalg.solve` (or a factorization) over `inv(a) @ b`.
- NumPy/SciPy use multithreaded BLAS. Control the thread count with
  `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` when benchmarking or
  running several processes at once.
