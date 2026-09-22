# api-fetcher

A small Python script and library for fetching JSON data from a REST API over HTTP.

## Requirements

- Python 3.10+
- [`requests`](https://pypi.org/project/requests/)

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development (tests and linting):

```bash
pip install -e ".[dev]"
```

## Usage

Command line:

```bash
api-fetcher https://api.example.com/users -p page=2 -H "Accept: application/json"
```

As a library:

```python
from api_fetcher import ApiClient

with ApiClient("https://api.example.com", headers={"Accept": "application/json"}) as client:
    users = client.get("users", params={"page": 2})
```

`ApiClient` retries transient failures (429/5xx), applies a configurable timeout, and
raises `ApiError` for connection problems, non-2xx responses, or invalid JSON.

## Development

```bash
pytest
ruff check .
```
