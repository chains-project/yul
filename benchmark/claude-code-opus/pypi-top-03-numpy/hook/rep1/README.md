# numcompute

Script for heavy numerical array and matrix computations, built on NumPy and SciPy.

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
uv run ruff check . && uv run ruff format .
```

## Performance notes

- Keep work vectorized; avoid Python-level loops over array elements.
- NumPy/SciPy delegate to a multithreaded BLAS (OpenBLAS by default). Control threads with
  `OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS`. Check the backend with
  `python -c "import numpy; numpy.show_config()"`.
- Prefer factor-and-solve (`cho_factor`, `lu_factor`) over explicit `inv()`.
