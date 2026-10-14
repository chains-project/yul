# numcompute

Numerical array and matrix computations with NumPy and SciPy.

## Setup

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
uv run ruff check .
uv run ruff format .
```

## Performance notes

- NumPy/SciPy delegate dense linear algebra to a BLAS/LAPACK backend (OpenBLAS in the
  PyPI wheels). Check which one is in use with `uv run python -c "import numpy; numpy.show_config()"`.
- Control BLAS thread count with `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS`.
- Prefer vectorized operations and in-place updates (`out=`) over Python loops.
