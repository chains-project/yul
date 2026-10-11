# matcomp

Heavy numerical array and matrix computations with NumPy.

## Setup

Uses [uv](https://docs.astral.sh/uv/) for environment and dependency management.

```bash
uv sync              # create .venv and install numpy + dev tools
```

## Usage

```bash
uv run python -m matcomp bench --size 2048      # time matmul and Gram matrix
uv run python -m matcomp dominant --size 128    # power-iteration eigenvalue
```

As a library:

```python
import numpy as np
from matcomp import matmul, gram_matrix, solve, power_iteration

a = np.random.default_rng(0).standard_normal((1000, 1000))
b = matmul(a, a.T)
g = gram_matrix(a)
```

## Testing

```bash
uv run pytest
```

## Notes on performance

NumPy delegates `@`, `A.T @ A`, and `numpy.linalg.*` to a multithreaded BLAS
backend. For very large workloads, keep arrays C-contiguous, batch operations,
and prefer `float64` (or `float32` to halve memory traffic). If you later need
GPU/autodiff, the `matcomp.core` interface is a drop-in seam for a JAX or CuPy
backend.
