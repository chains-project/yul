# api-client

Fetch JSON data from a REST API over HTTP.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended)

## Setup

```bash
uv sync --extra dev
cp .env.example .env   # then edit API_BASE_URL / API_TOKEN
```

## Usage

As a command line tool:

```bash
uv run api-client /users
uv run api-client /search -p q=python -p page=1
uv run api-client --base-url https://api.example.com /health
```

As a library:

```python
from api_client import APIClient

with APIClient("https://api.example.com", token="...") as client:
    users = client.get_json("/users", params={"page": 1})
```

Configuration is read from the environment: `API_BASE_URL` (required),
`API_TOKEN`, `API_TIMEOUT`, `API_RETRIES`.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```
