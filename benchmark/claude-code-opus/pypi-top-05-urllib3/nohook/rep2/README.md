# http-client

Python script using [urllib3](https://urllib3.readthedocs.io/) for low-level HTTP control:
connection pooling (`PoolManager`), automatic retries with backoff (`Retry`), and separate
connect/read timeouts.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run http-client https://example.com https://example.org -v
```

Tune pooling/retry behaviour via `ClientConfig` in `src/http_client/client.py`, or use it in code:

```python
from http_client import ClientConfig, build_pool_manager

http = build_pool_manager(ClientConfig(maxsize=20, total_retries=5, backoff_factor=1.0))
resp = http.request("GET", "https://example.com")
```
