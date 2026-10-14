# http-client

A small HTTP script built directly on [urllib3](https://urllib3.readthedocs.io/),
which gives explicit control over connection pooling, timeouts, and retries.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run http-client https://example.com -v
uv run http-client https://httpbin.org/status/503 --retries 2 -v
```

Pool and retry settings are in `src/http_client/client.py`.

## Tests

```sh
uv run pytest
```
