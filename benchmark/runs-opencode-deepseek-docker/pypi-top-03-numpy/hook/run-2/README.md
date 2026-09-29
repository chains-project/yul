# matrixlab

Heavy numerical array and matrix computations in Python, built on NumPy and SciPy.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

As a library:

```python
from matrixlab import solve_linear_system, matmul_blocked

A = [[4.0, 1.0], [1.0, 3.0]]
b = [1.0, 2.0]
x = solve_linear_system(A, b)
```

From the command line:

```bash
matrixlab --size 512 --op matmul
```

## Development

```bash
pytest
ruff check .
```
