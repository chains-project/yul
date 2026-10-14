# httptool

A script with low-level control over HTTP connections, built on
[urllib3](https://urllib3.readthedocs.io/): connection pooling, automatic
retries with exponential backoff, and separate connect/read timeouts.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run httptool https://example.com https://example.org -v
uv run httptool --retries 5 --backoff 1 --pool-size 4 https://example.com
```

From Python:

```python
from httptool import ClientConfig, build_pool_manager

http = build_pool_manager(ClientConfig(maxsize=20, total_retries=5))
resp = http.request("GET", "https://example.com")
```

All tuning lives in `ClientConfig` (`src/httptool/client.py`). By default,
retries apply only to idempotent methods and to statuses 429/500/502/503/504,
and `Retry-After` headers are respected.

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
```
