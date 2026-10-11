# api-fetcher

A small Python script/library for fetching JSON data from a REST API over HTTP.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup

```bash
uv sync
```

This creates a `.venv` and installs runtime and dev dependencies.

## Usage

As a command-line script:

```bash
uv run api-fetcher https://api.example.com/users
uv run api-fetcher https://api.example.com/search -p q=python -H "Authorization:Bearer TOKEN"
```

As a library:

```python
from api_fetcher import fetch

response = fetch("https://api.example.com/users", params={"page": 1})
print(response.data)
```

`fetch()` parses the JSON body and raises `ApiError` on HTTP errors, connection
failures, or non-JSON responses.

## Development

```bash
uv run pytest
```
