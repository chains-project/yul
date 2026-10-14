# httpclient

A script for fetching URLs with low-level HTTP control, built directly on
[urllib3](https://urllib3.readthedocs.io/).

- **Connection pooling**: `PoolManager` keeps one pool per host, with
  keep-alive connections. `maxsize` sets the pool size and `block=True` caps
  concurrency per host.
- **Automatic retries**: `Retry` with exponential backoff on connection and
  read errors and on 429/500/502/503/504. It honors `Retry-After`. Only
  idempotent methods are retried.
- **Timeouts**: separate connect and read timeouts.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run httpclient https://example.com https://example.org -v
uv run httpclient --retries 3 --backoff 1.0 --pool-size 4 https://httpbin.org/status/503
```

`-v` turns on urllib3's DEBUG logging, which shows new connections being
opened and each retry.

## Tests

```sh
uv run pytest
```

## Layout

- `src/httpclient/client.py`: `build_pool_manager()` and `build_retry()`. Tune pooling and retry policy here.
- `src/httpclient/cli.py`: the command-line entry point.
