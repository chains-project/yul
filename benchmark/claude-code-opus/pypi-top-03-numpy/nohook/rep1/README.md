# numcompute

Numerical array and matrix computations built on NumPy and SciPy.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```sh
uv sync
```

## Usage

```sh
uv run numcompute --size 4000
```

## Development

```sh
uv run pytest
uv run ruff check . && uv run ruff format .
```

## Performance notes

- NumPy/SciPy use a multithreaded BLAS/LAPACK (OpenBLAS by default with the wheels).
  Control thread count with `OPENBLAS_NUM_THREADS` / `OMP_NUM_THREADS`.
- Inspect the BLAS backend with `uv run python -c "import numpy; numpy.show_config()"`.
- Prefer vectorized operations and in-place updates (`out=`) over Python loops on large arrays.
