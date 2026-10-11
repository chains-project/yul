# numcompute

Numerical array and matrix computation toolkit built on
[NumPy](https://numpy.org/) and [SciPy](https://scipy.org/).

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --dev          # core + development tooling
uv sync --extra accel  # optional Numba JIT acceleration
```

## Usage

```python
import numcompute as nc

a = nc.random_spd(512, seed=0)
b = nc.random_spd(512, seed=1)

c = nc.matmul(a, b)
x = nc.solve(a, c)
sv = nc.singular_values(a)
```

## Benchmark CLI

```bash
uv run numcompute --size 2048
# or
uv run python -m numcompute
```

## Development

```bash
uv run pytest           # tests + coverage
uv run ruff check .     # lint
uv run ruff format .    # format
uv run mypy             # type check
```
