# http-client

Script for making HTTP requests with explicit connection pooling and automatic retries, using [urllib3](https://urllib3.readthedocs.io/).

## Setup

```sh
uv sync
```

## Usage

```sh
uv run http-client https://example.com https://example.org --retries 3 --pool-size 5
```

## Tests

```sh
uv run pytest
```

## Where to tune things

All in `src/http_client/client.py`:

- `build_pool_manager` sets how many host pools there are, how many connections each keeps, whether to block when a pool is full, and the timeouts.
- `build_retry` sets the retry count, backoff, which status codes get retried, and whether to honour `Retry-After`.
