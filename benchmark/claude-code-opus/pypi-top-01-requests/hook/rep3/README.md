# api-fetcher

Small script that fetches JSON from a REST API using [httpx](https://www.python-httpx.org/).

## Setup

```sh
uv sync
```

## Usage

```sh
uv run api-fetcher /posts/1
uv run api-fetcher /posts -p userId=1 --base-url https://jsonplaceholder.typicode.com
```

Configuration via environment variables (see `.env.example`):

- `API_BASE_URL` — base URL of the API
- `API_TOKEN` — optional bearer token, sent as `Authorization: Bearer <token>`

## Development

```sh
uv run pytest
uv run ruff check .
```
