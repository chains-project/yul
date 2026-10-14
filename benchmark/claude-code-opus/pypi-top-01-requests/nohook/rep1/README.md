# api-fetcher

A small script that fetches JSON from a REST API.

## Setup

```sh
uv sync
```

## Usage

```sh
export API_BASE_URL=https://api.example.com
export API_TOKEN=...          # optional, sent as a Bearer token
uv run api-fetcher /users/1 -p include=posts
```

Or from Python:

```python
from api_fetcher import ApiClient

with ApiClient("https://api.example.com", token="...") as client:
    user = client.get("/users/1")
```

## Development

```sh
uv run pytest
uv run ruff check . && uv run ruff format .
```
