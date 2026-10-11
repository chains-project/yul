# numerics

A Python project for heavy numerical array and matrix computations, built on
[NumPy](https://numpy.org/) and [SciPy](https://scipy.org/).

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup

```bash
uv sync              # core dependencies (numpy, scipy)
uv sync --extra dev  # plus test/lint tooling
uv sync --extra jit  # plus Numba JIT (optional)
uv sync --extra gpu  # plus CuPy for CUDA GPUs (optional)
```

## Usage

Run the demo script:

```bash
uv run numerics
# or
uv run python -m numerics
```

Use the core routines directly:

```python
import numpy as np
from numerics import matmul, solve, eigenvalues

a = np.random.default_rng(0).random((256, 256))
b = np.random.default_rng(1).random((256, 256))
c = matmul(a, b)
```

## Performance notes

- Link NumPy/SciPy against an optimized BLAS/LAPACK (OpenBLAS, MKL, BLIS) for
  multi-threaded CPU matrix operations.
- Use `float32`/`complex64` or blocked/out-of-core algorithms when problems
  exceed memory.
- Reach for the `jit` extra (Numba) for tight Python loops, and the `gpu` extra
  (CuPy) for large dense linear algebra on NVIDIA hardware.

## Development

```bash
uv run pytest
uv run ruff check .
```
