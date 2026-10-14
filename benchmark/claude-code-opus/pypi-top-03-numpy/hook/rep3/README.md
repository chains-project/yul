# numcompute

Numerical array and matrix computations built on NumPy and SciPy.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run numcompute --size 2000
```

## Development

```sh
uv run pytest
uv run ruff check . && uv run ruff format .
```

## Performance notes

- Write vectorized NumPy code; avoid Python loops over array elements.
- Dense linear algebra runs on the BLAS/LAPACK bundled with the NumPy/SciPy wheels
  (OpenBLAS). Control threading with `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS`.
- Prefer `scipy.linalg.solve` / factorizations over computing explicit inverses.
