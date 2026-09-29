# numerical

Heavy numerical array and matrix computations built on NumPy and SciPy.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
numerical --size 1000
```

Or from Python:

```python
from numerical.compute import matmul, solve_linear_system

a = [[4.0, 1.0], [1.0, 3.0]]
b = [1.0, 2.0]
print(matmul(a, b))
print(solve_linear_system(a, b))
```

## Tests

```bash
pytest
```
