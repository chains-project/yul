# http-client

Low-level HTTP client built on [urllib3](https://urllib3.readthedocs.io/), providing:

- **Connection pooling** via `PoolManager` (per-host connection reuse, `maxsize`, optional `block`).
- **Automatic retries** with exponential backoff, honoring `Retry-After`.

## Setup

```bash
uv sync
```

## Usage

```python
from http_client import HttpClient, build_retries

retries = build_retries(total=5, backoff_factor=0.5)
with HttpClient(retries=retries, timeout=10.0, maxsize=20) as client:
    resp = client.get("https://example.com")
    print(resp.status, resp.data[:80])
```

CLI:

```bash
uv run http-client https://example.com
```

## Development

```bash
uv run pytest
```
