# api-fetcher

A small CLI that fetches JSON from a REST API.

## Setup

```sh
uv sync
```

## Usage

```sh
export API_BASE_URL=https://api.example.com
export API_TOKEN=...          # optional, sent as a Bearer token
uv run api-fetcher /users
```

Options: `--base-url`, `--timeout`, `-v/--verbose`.

## Development

```sh
uv run pytest
uv run ruff check .
```
