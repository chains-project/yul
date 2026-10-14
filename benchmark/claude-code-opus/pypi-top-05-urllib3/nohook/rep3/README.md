# httpclient

A script with low-level control over HTTP connections, built on [urllib3](https://urllib3.readthedocs.io/):

- **Connection pooling**: `urllib3.PoolManager` keeps a pool of keep-alive connections per host (`num_pools`, `maxsize`, `block`).
- **Automatic retries**: `urllib3.util.Retry` with exponential backoff, retries on 429/5xx, and `Retry-After` support.
- **Timeouts**: separate connect and read timeouts.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run httpclient https://example.com https://httpbin.org/status/503 -v
```

To use it as a library, import `build_pool_manager` / `build_retry` from `httpclient`.

## Tests

```sh
uv run pytest
```
