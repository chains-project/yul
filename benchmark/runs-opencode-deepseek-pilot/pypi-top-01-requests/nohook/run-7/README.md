# rest-fetcher

A small Python project that fetches data from a REST API over HTTP.

## Setup

```bash
uv sync
```

## Usage

Fetch JSON from any endpoint:

```bash
uv run rest-fetcher https://api.example.com/items
```

Or from Python:

```python
from rest_fetcher import fetch_json

data = fetch_json("https://api.example.com/items", params={"limit": 10})
```

## Development

```bash
uv sync --extra dev
uv run pytest
```
