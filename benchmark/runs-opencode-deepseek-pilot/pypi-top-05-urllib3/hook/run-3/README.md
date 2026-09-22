# httpclient

Low-level HTTP client built on [urllib3](https://urllib3.readthedocs.io/)
providing connection pooling and automatic retries.

## Usage

```python
from httpclient import HttpClient

client = HttpClient(
    pool_connections=10,   # number of host connection pools
    pool_maxsize=10,       # connections kept per host pool
    max_retries=3,         # automatic retries on failure
    backoff_factor=0.5,    # exponential backoff between retries
    timeout=10.0,
)

resp = client.request("GET", "https://httpbin.org/get")
print(resp.status, resp.data)
client.close()
```

Or as a context manager:

```python
with HttpClient() as client:
    resp = client.get("https://httpbin.org/get")
```

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
```
