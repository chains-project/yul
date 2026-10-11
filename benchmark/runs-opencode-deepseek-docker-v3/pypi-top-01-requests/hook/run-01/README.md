# api-fetcher

Fetch data from a REST API over HTTP.

## Setup

```bash
uv sync
cp .env.example .env  # then edit it
```

## Usage

As a CLI:

```bash
uv run api-fetcher /users/1 --base-url https://api.example.com
uv run api-fetcher /search -p q=hello -H X-Trace=abc --token "$API_TOKEN"
```

Or from Python:

```python
from api_fetcher import fetch

data = fetch("/users/1", base_url="https://api.example.com")
```

Configuration is read from the environment when not passed explicitly:

- `API_BASE_URL` — base URL for relative paths.
- `API_TOKEN` — sent as `Authorization: Bearer <token>`.

## Development

```bash
uv run pytest
uv run ruff check .
```
