# api-fetcher

A small script that fetches JSON from a REST API over HTTP and prints it.

## Setup

```sh
uv sync
```

## Usage

```sh
export API_BASE_URL=https://api.example.com
export API_TOKEN=...            # optional, sent as a Bearer token

uv run api-fetcher /users/1
uv run api-fetcher /search -p q=python -p limit=10
```

You can pass `--base-url` instead of setting `API_BASE_URL`.

## Development

```sh
uv run pytest
uv run ruff check .
uv run ruff format .
```
