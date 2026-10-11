# numcompute

Heavy numerical array and matrix computations, built on NumPy and SciPy.

## Setup

```bash
uv sync
```

## Usage

As a library:

```python
import numpy as np
from numcompute import core

a = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])
x = core.solve(a, b)
```

As a script:

```bash
uv run numcompute --size 8
```

## Development

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```
