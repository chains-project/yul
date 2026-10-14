# api-fetcher

A small script that fetches JSON from a REST API over HTTP, built on [httpx](https://www.python-httpx.org/).

## Setup

```sh
uv sync
```

## Usage

```sh
export API_BASE_URL=https://api.example.com
export API_TOKEN=...            # optional, sent as a Bearer token

uv run api-fetcher /users/1
uv run api-fetcher /items -p page=2 -p limit=50 -o items.json
uv run api-fetcher --base-url https://jsonplaceholder.typicode.com /todos/1 -v
```

The exit code is 0 on success and 1 on HTTP, network, or JSON decode errors.
Connection failures are retried up to 3 times; requests time out after 10s (`--timeout`).

## Development

```sh
uv run pytest
uv run ruff check . && uv run ruff format .
```
