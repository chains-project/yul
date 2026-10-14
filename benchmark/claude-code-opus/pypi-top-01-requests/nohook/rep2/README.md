# api-fetcher

A small script that fetches JSON from a REST API over HTTP(S).

## Setup

```sh
uv sync
```

## Usage

```sh
export API_BASE_URL=https://api.example.com
export API_TOKEN=...            # optional, sent as a Bearer token
uv run api-fetcher /users/1 -p include=posts
```

## Development

```sh
uv run pytest
uv run ruff check .
```
