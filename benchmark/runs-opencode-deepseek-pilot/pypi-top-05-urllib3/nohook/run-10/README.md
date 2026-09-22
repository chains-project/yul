# httpclient

A small HTTP client built on [urllib3](https://urllib3.readthedocs.io/) that
gives direct, low-level control over HTTP connections:

- **Connection pooling** via `urllib3.PoolManager` — per-host pools with a
  configurable `num_pools` / `maxsize` and optional blocking.
- **Automatic retries** via `urllib3.util.Retry` — exponential backoff,
  connection/read/status retries, `Retry-After` support, and a configurable
  status and method allow-list.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Usage

```python
from httpclient import HttpClient

with HttpClient(num_pools=20, maxsize=20, retries=5, backoff_factor=0.5) as client:
    data = client.get_json("https://httpbin.org/get")
    print(data)
```

### Command line

```bash
httpclient https://httpbin.org/get
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```
