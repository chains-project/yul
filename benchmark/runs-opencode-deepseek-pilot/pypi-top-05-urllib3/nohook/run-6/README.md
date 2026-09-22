# http-client

A small, low-level HTTP client built on [urllib3](https://urllib3.readthedocs.io/).
It keeps a pool of reusable connections and retries transient failures with
exponential backoff, while returning the raw `urllib3` response so callers
retain full control over the wire-level details.

## Features

- **Connection pooling** — one `PoolManager` caches connection pools per host,
  so repeated requests reuse TCP connections.
- **Automatic retries** — configurable retries for connection, read, redirect
  and status failures, with exponential backoff and `Retry-After` support.
- **Low-level control** — `request()` passes keyword arguments straight to
  `PoolManager.request` (`fields`, `body`, `redirect`, `preload_content`, ...)
  and returns the raw `HTTPResponse`.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup

```bash
uv sync
```

This creates `.venv` and installs `urllib3` plus the development dependencies.

## Usage

```bash
# Fetch a URL (retries transient 5xx/429 responses by default)
uv run http-client https://example.com

# Tune retries, backoff and timeout
uv run http-client https://example.com --retries 5 --backoff 1.0 --timeout 5
```

As a library:

```python
from http_client import HttpClient

with HttpClient(total_retries=3, backoff_factor=0.5, timeout=10.0) as client:
    response = client.get("https://example.com")
    print(response.status, response.headers.get("content-type"))
    print(response.data[:100])

    # Low-level knobs are still available:
    response = client.request(
        "POST",
        "https://example.com/api",
        fields={"key": "value"},
        redirect=False,
        preload_content=False,
    )
    response.release_conn()
```

## Development

```bash
uv run pytest        # run the test suite
```

Tests spin up a local threaded HTTP server and assert retry and
connection-reuse behaviour; no external network access is required.
