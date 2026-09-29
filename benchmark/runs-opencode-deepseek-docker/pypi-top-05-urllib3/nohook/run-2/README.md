# httptool

A small Python project for scripts that need low-level control over HTTP
connections: keep-alive connection pooling and automatic retries.

Built on [`urllib3`](https://urllib3.readthedocs.io/), which exposes the
connection pool and retry policy directly instead of hiding them behind a
higher-level session abstraction.

## Layout

```
src/httptool/
  __init__.py    package exports
  client.py      pooling + retry configuration
  __main__.py    runnable CLI (`python -m httptool URL`)
tests/           pytest suite (no network access required)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

As a script:

```bash
httptool https://example.com https://example.org
# or
python -m httptool https://example.com
```

Programmatically:

```python
from httptool import ClientConfig

config = ClientConfig(total_retries=5, backoff_factor=1.0, max_pool_size=20)
http = config.build_pool_manager()
try:
    response = http.request("GET", "https://example.com", preload_content=False)
    print(response.status)
    response.release_conn()
finally:
    http.clear()
```

## Configuration

`ClientConfig` controls both pooling and retries:

| Field | Default | Purpose |
| --- | --- | --- |
| `total_retries` | `3` | Retries for connect/read/status failures |
| `backoff_factor` | `0.5` | Exponential backoff base between retries |
| `connect_timeout` | `5.0` | Seconds to establish a connection |
| `read_timeout` | `30.0` | Seconds to wait for a response |
| `max_pool_size` | `10` | Max kept-alive connections per host |
| `pool_block` | `False` | Block instead of discarding when pool is full |

Retries apply to `GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`, `TRACE` and the
status codes `429, 500, 502, 503, 504`, honoring `Retry-After` headers.
Idempotency matters: methods like `POST` are intentionally excluded.

## Tests

```bash
pytest
ruff check .
```
