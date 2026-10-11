# http-client

Low-level HTTP client built on [urllib3](https://urllib3.readthedocs.io/), giving
direct control over connection pooling and automatic retries.

## Setup

```sh
uv sync
```

## Usage

```python
from http_client import HttpClient, PoolConfig, RetryPolicy

pool = PoolConfig(
    num_pools=10,  # distinct host pools kept in the manager
    maxsize=20,  # max keep-alive connections per host
    block=True,  # wait instead of dropping when the pool is full
    retries=RetryPolicy(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "PUT", "DELETE"}),
    ),
)

with HttpClient(pool=pool, timeout=10.0, verify=True) as client:
    response = client.get("https://example.com/")
    print(response.status, response.data)
    response.release_conn()
```

`RetryPolicy` covers connection, read and status failures; `PoolConfig` tunes
the number of pools, per-host connection limit and blocking behaviour.

## CLI

```sh
uv run http-client https://example.com/ --retries 5 --maxsize 20
```

## Tests

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
